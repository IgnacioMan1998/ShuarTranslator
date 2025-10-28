"""User repository interface for admin functionality."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.features.feedback.domain.entities.feedback import UserRole


class IUserRepository(ABC):
    """Interface for User repository for admin operations."""
    
    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """Find user by ID."""
        pass
    
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find user by email address."""
        pass
    
    @abstractmethod
    async def find_by_role(self, role: UserRole) -> List[Dict[str, Any]]:
        """Find users by their role."""
        pass
    
    @abstractmethod
    async def find_verified_speakers(self) -> List[Dict[str, Any]]:
        """Find verified Shuar speakers."""
        pass
    
    @abstractmethod
    async def find_experts(self) -> List[Dict[str, Any]]:
        """Find linguistic experts."""
        pass
    
    @abstractmethod
    async def find_active_contributors(
        self, 
        since: datetime, 
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Find users who have been active contributors since a date."""
        pass
    
    @abstractmethod
    async def get_user_statistics(self, user_id: UUID) -> Dict[str, Any]:
        """Get comprehensive statistics for a user."""
        pass
    
    @abstractmethod
    async def get_user_contributions(self, user_id: UUID) -> Dict[str, Any]:
        """Get user's contributions (words added, feedback given, etc.)."""
        pass
    
    @abstractmethod
    async def update_user_role(self, user_id: UUID, new_role: UserRole) -> bool:
        """Update a user's role."""
        pass
    
    @abstractmethod
    async def verify_as_native_speaker(self, user_id: UUID) -> bool:
        """Mark a user as a verified native Shuar speaker."""
        pass
    
    @abstractmethod
    async def get_user_activity_log(
        self, 
        user_id: UUID, 
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get user's activity log."""
        pass
    
    @abstractmethod
    async def count_by_role(self, role: UserRole) -> int:
        """Count users by role."""
        pass
    
    @abstractmethod
    async def count_verified_speakers(self) -> int:
        """Count verified native speakers."""
        pass
    
    @abstractmethod
    async def get_user_engagement_metrics(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get user engagement metrics for a date range."""
        pass