"""Dependency injection container configuration."""

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide

from src.shared.config.settings import settings
from src.infrastructure.external.supabase_client import SupabaseClient


class Container(containers.DeclarativeContainer):
    """IoC container for dependency injection."""
    
    # Configuration
    config = providers.Configuration()
    
    # External services
    supabase_client = providers.Singleton(
        SupabaseClient,
        url=settings.supabase_url,
        key=settings.supabase_anon_key,
        service_role_key=settings.supabase_service_role_key
    )
    
    # Repositories will be added as we implement them
    
    # Domain services will be added as we implement them
    
    # Use cases will be added as we implement them


# Global container instance
container = Container()