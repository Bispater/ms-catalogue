"""
Formateador de monedas para diferentes países
"""
from decimal import Decimal
from typing import Optional, Dict, Union


class CurrencyConfig:
    """Configuración de formato para una moneda específica"""
    
    def __init__(
        self,
        code: str,
        symbol: str,
        decimals: int,
        decimal_separator: str,
        thousands_separator: str,
        symbol_position: str = 'prefix',  # 'prefix' o 'suffix'
        space_between: bool = True
    ):
        self.code = code
        self.symbol = symbol
        self.decimals = decimals
        self.decimal_separator = decimal_separator
        self.thousands_separator = thousands_separator
        self.symbol_position = symbol_position
        self.space_between = space_between


class CurrencyFormatter:
    """
    Formateador de precios según diferentes monedas y países
    
    Uso:
        formatter = CurrencyFormatter()
        formatted = formatter.format(1200000, 'CLP')
        # Resultado: "1.200.000"
    """
    
    # Configuraciones de monedas
    CURRENCIES: Dict[str, CurrencyConfig] = {
        'CLP': CurrencyConfig(
            code='CLP',
            symbol='$',
            decimals=0,
            decimal_separator=',',
            thousands_separator='.',
            symbol_position='prefix',
            space_between=True
        ),
        'USD': CurrencyConfig(
            code='USD',
            symbol='$',
            decimals=2,
            decimal_separator='.',
            thousands_separator=',',
            symbol_position='prefix',
            space_between=False
        ),
        'EUR': CurrencyConfig(
            code='EUR',
            symbol='€',
            decimals=2,
            decimal_separator=',',
            thousands_separator='.',
            symbol_position='suffix',
            space_between=True
        ),
        'ARS': CurrencyConfig(
            code='ARS',
            symbol='$',
            decimals=2,
            decimal_separator=',',
            thousands_separator='.',
            symbol_position='prefix',
            space_between=True
        ),
        'BRL': CurrencyConfig(
            code='BRL',
            symbol='R$',
            decimals=2,
            decimal_separator=',',
            thousands_separator='.',
            symbol_position='prefix',
            space_between=True
        ),
        'MXN': CurrencyConfig(
            code='MXN',
            symbol='$',
            decimals=2,
            decimal_separator='.',
            thousands_separator=',',
            symbol_position='prefix',
            space_between=True
        ),
        'COP': CurrencyConfig(
            code='COP',
            symbol='$',
            decimals=0,
            decimal_separator=',',
            thousands_separator='.',
            symbol_position='prefix',
            space_between=True
        ),
        'PEN': CurrencyConfig(
            code='PEN',
            symbol='S/',
            decimals=2,
            decimal_separator='.',
            thousands_separator=',',
            symbol_position='prefix',
            space_between=False
        ),
    }
    
    @classmethod
    def format(
        cls,
        amount: Optional[Union[float, Decimal, int]],
        currency_code: str = 'CLP',
        include_symbol: bool = False
    ) -> Optional[str]:
        """
        Formatea un monto según la configuración de la moneda
        
        Args:
            amount: Monto a formatear
            currency_code: Código de moneda (CLP, USD, EUR, etc.)
            include_symbol: Si incluir el símbolo de moneda
        
        Returns:
            String formateado o None si amount es None
        
        Examples:
            >>> CurrencyFormatter.format(1200000, 'CLP')
            '1.200.000'
            
            >>> CurrencyFormatter.format(1200000, 'CLP', include_symbol=True)
            '$ 1.200.000'
            
            >>> CurrencyFormatter.format(1200.50, 'USD')
            '1,200.50'
            
            >>> CurrencyFormatter.format(1200.50, 'EUR', include_symbol=True)
            '1.200,50 €'
        """
        if amount is None:
            return None
        
        # Obtener configuración de moneda
        config = cls.CURRENCIES.get(currency_code)
        
        if not config:
            # Si no existe configuración, usar formato por defecto
            return cls._format_default(amount)
        
        # Convertir a float
        amount_float = float(amount)
        
        # Formatear según decimales
        if config.decimals == 0:
            # Sin decimales
            amount_int = int(round(amount_float))
            formatted_number = f"{amount_int:,}"
        else:
            # Con decimales
            formatted_number = f"{amount_float:,.{config.decimals}f}"
        
        # Reemplazar separadores por defecto (Python usa , para miles y . para decimales)
        # Primero, reemplazar temporalmente
        formatted_number = formatted_number.replace(',', 'TEMP_THOUSANDS')
        formatted_number = formatted_number.replace('.', 'TEMP_DECIMAL')
        
        # Ahora aplicar los separadores correctos
        formatted_number = formatted_number.replace('TEMP_THOUSANDS', config.thousands_separator)
        formatted_number = formatted_number.replace('TEMP_DECIMAL', config.decimal_separator)
        
        # Agregar símbolo si se solicita
        if include_symbol:
            space = ' ' if config.space_between else ''
            if config.symbol_position == 'prefix':
                formatted_number = f"{config.symbol}{space}{formatted_number}"
            else:
                formatted_number = f"{formatted_number}{space}{config.symbol}"
        
        return formatted_number
    
    @classmethod
    def _format_default(cls, amount: Union[float, Decimal, int]) -> str:
        """Formato por defecto si no existe configuración de moneda"""
        amount_float = float(amount)
        return f"{amount_float:.2f}"
    
    @classmethod
    def get_currency_info(cls, currency_code: str) -> Optional[Dict]:
        """
        Obtiene información de una moneda
        
        Returns:
            Dict con información de la moneda o None si no existe
        """
        config = cls.CURRENCIES.get(currency_code)
        if not config:
            return None
        
        return {
            'code': config.code,
            'symbol': config.symbol,
            'decimals': config.decimals,
            'decimal_separator': config.decimal_separator,
            'thousands_separator': config.thousands_separator,
            'symbol_position': config.symbol_position,
        }
    
    @classmethod
    def get_available_currencies(cls) -> list:
        """Retorna lista de códigos de monedas disponibles"""
        return list(cls.CURRENCIES.keys())
