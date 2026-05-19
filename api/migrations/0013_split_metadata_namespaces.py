"""
Migración de datos: reorganiza ClientConfiguration.metadata en dos namespaces
independientes: "theme" (estilos visuales) y "texts" (copys del UI).

Antes (esquema plano, ambiguo):
    metadata = {
        "global": {...},          # estilos
        "welcome": {              # ¡mezcla!
            "title": {color: ...},  # estilo
            "subtitle": "Coct..."   # texto (a veces, según cliente)
        }
    }

Después (separado):
    metadata = {
        "theme": {
            "global": {...},
            "welcome": {"title": {color: ...}, "subtitle": {color: ...}},
            ...
        },
        "texts": {
            "welcome": {"tagline": "...", "subtitle": "...", ...},
            "category": {"title": "...", "subtitle": "..."}
        }
    }

Idempotente: si una ClientConfiguration ya está migrada (tiene "theme" en la raíz),
no se toca. La migración inversa restaura el esquema plano viejo desde "theme".
"""

from django.db import migrations


# Subset de claves que pertenecen al namespace `theme` en el esquema viejo.
# Cualquier otra clave de la raíz se deja donde está (probablemente custom del cliente).
THEME_KEYS = (
    "global",
    "welcome",
    "home",
    "productModal",
    "cartFloating",
    "checkout",
    "payment",
    "confirmModal",
)

# Mapeo de keys de texto del esquema viejo (planas con guión bajo) al nuevo (anidadas).
# Si el cliente había seteado "texts.category_title" lo movemos a "texts.category.title".
LEGACY_TEXT_REMAP = {
    "category_title": ("category", "title"),
    "category_subtitle": ("category", "subtitle"),
}

# Claves dentro de "welcome" (esquema viejo) que en realidad son TEXTOS (no estilos)
# y deben extraerse a "texts.{section}.{field}" en vez de ir a "theme.welcome".
# Cubre el caso donde un cliente Midnight ya había seteado overrides como strings.
WELCOME_TEXT_FIELDS = {
    "tagline": ("welcome", "tagline"),
    "subtitle": ("welcome", "subtitle"),
    "ctaLabel": ("welcome", "ctaLabel"),
    "statusLabel": ("welcome", "statusLabel"),
    "fallbackVideoUrl": ("idle", "videoFallbackUrl"),
}


def split_metadata(apps, schema_editor):
    ClientConfiguration = apps.get_model("api", "ClientConfiguration")
    # Import diferido para no acoplar la migración al import time del template.
    from api.default_template import DEFAULT_TEMPLATE

    default_texts = DEFAULT_TEMPLATE.get("texts", {})

    for cfg in ClientConfiguration.objects.all():
        metadata = cfg.metadata or {}

        # Ya migrada: respetar y seguir.
        if isinstance(metadata.get("theme"), dict):
            # Solo asegurar que "texts" exista para que getMetadata no falle.
            if not isinstance(metadata.get("texts"), dict):
                metadata["texts"] = dict(default_texts)
                cfg.metadata = metadata
                cfg.save(update_fields=["metadata"])
            continue

        new_theme = {}
        new_texts = _deep_copy(default_texts)
        leftovers = {}

        for key, value in metadata.items():
            if key == "welcome" and isinstance(value, dict):
                # `welcome` mezcla estilos y textos. Separar antes de archivar.
                welcome_styles = {}
                for wk, wv in value.items():
                    if wk in WELCOME_TEXT_FIELDS and isinstance(wv, str) and wv:
                        section, field = WELCOME_TEXT_FIELDS[wk]
                        new_texts.setdefault(section, {})[field] = wv
                    else:
                        welcome_styles[wk] = wv
                if welcome_styles:
                    new_theme["welcome"] = welcome_styles
            elif key in THEME_KEYS:
                new_theme[key] = value
            elif key == "texts" and isinstance(value, dict):
                # Mover los textos del cliente sobre los defaults; respetar lo del cliente.
                for tk, tv in value.items():
                    if tk in LEGACY_TEXT_REMAP:
                        section, field = LEGACY_TEXT_REMAP[tk]
                        new_texts.setdefault(section, {})[field] = tv
                    else:
                        # Texto custom no contemplado: lo guardamos tal cual.
                        new_texts[tk] = tv
            else:
                # Cualquier otra cosa (custom del cliente) se preserva en la raíz.
                leftovers[key] = value

        new_metadata = {"theme": new_theme, "texts": new_texts, **leftovers}
        cfg.metadata = new_metadata
        cfg.save(update_fields=["metadata"])


def merge_metadata(apps, schema_editor):
    """Revierte el split: aplana `theme.*` a la raíz y deja `texts` plano viejo."""
    ClientConfiguration = apps.get_model("api", "ClientConfiguration")

    inverse_text_remap = {v: k for k, v in LEGACY_TEXT_REMAP.items()}

    for cfg in ClientConfiguration.objects.all():
        metadata = cfg.metadata or {}
        theme = metadata.get("theme")
        texts = metadata.get("texts")

        # No estaba migrada: nada que revertir.
        if not isinstance(theme, dict) and not isinstance(texts, dict):
            continue

        rebuilt = {}

        if isinstance(theme, dict):
            for k, v in theme.items():
                rebuilt[k] = v

        if isinstance(texts, dict):
            flat_texts = {}
            for section, fields in texts.items():
                if isinstance(fields, dict):
                    for field, value in fields.items():
                        if (section, field) in inverse_text_remap:
                            flat_texts[inverse_text_remap[(section, field)]] = value
                        else:
                            # Sin remap conocido: usar guión bajo.
                            flat_texts[f"{section}_{field}"] = value
                else:
                    flat_texts[section] = fields
            if flat_texts:
                rebuilt["texts"] = flat_texts

        # Preservar claves leftover que no caían en theme/texts.
        for k, v in metadata.items():
            if k in ("theme", "texts"):
                continue
            rebuilt.setdefault(k, v)

        cfg.metadata = rebuilt
        cfg.save(update_fields=["metadata"])


def _deep_copy(value):
    if isinstance(value, dict):
        return {k: _deep_copy(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_deep_copy(v) for v in value]
    return value


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0012_rename_api_order_catalog_e6d9c5_idx_api_order_catalog_0bb97f_idx_and_more"),
    ]

    operations = [
        migrations.RunPython(split_metadata, reverse_code=merge_metadata),
    ]
