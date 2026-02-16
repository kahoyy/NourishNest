"""
Common Redis caching patterns for Django
Includes query caching, sessions, rate limiting, and leaderboards
"""
import logging
from typing import Optional, Any, Callable, List
from django.core.cache import cache
from django_redis import get_redis_connection

logger = logging.getLogger('cache_utils')


class QueryCache:
    """
    Query result caching pattern
    Cache database and API query results with easy invalidation
    """
    
    def __init__(self, default_ttl: int = 3600):
        """
        Initialize query cache
        :param default_ttl: Default TTL in seconds (1 hour)
        """
        self.default_ttl = default_ttl
    
    def get_or_execute(
        self,
        query_key: str,
        query_fn: Callable,
        ttl: Optional[int] = None
    ) -> Any:
        """
        Execute query with caching (cache-aside pattern)
        
        :param query_key: Unique key for the query
        :param query_fn: Callable that executes the actual query
        :param ttl: Optional custom TTL
        :return: Query results
        """
        # Try cache first
        cached = cache.get(query_key)
        if cached is not None:
            logger.debug(f"[QueryCache] HIT: {query_key}")
            return cached
        
        # Cache miss - execute query
        logger.debug(f"[QueryCache] MISS: {query_key} - executing query")
        result = query_fn()
        
        # Cache the result
        ttl = ttl or self.default_ttl
        cache.set(query_key, result, ttl)
        
        return result
    
    def invalidate(self, query_key: str) -> None:
        """
        Invalidate specific query cache
        
        :param query_key: Query key to invalidate
        """
        cache.delete(query_key)
        logger.debug(f"[QueryCache] INVALIDATE: {query_key}")
    
    def invalidate_by_pattern(self, pattern: str) -> int:
        """
        Invalidate multiple queries matching a pattern
        
        :param pattern: Pattern to match (e.g., "query:user:*")
        :return: Number of keys invalidated
        """
        redis_conn = get_redis_connection('default')
        keys = redis_conn.keys(pattern)
        
        if keys:
            redis_conn.delete(*keys)
            logger.debug(f"[QueryCache] INVALIDATE PATTERN: {pattern} ({len(keys)} keys)")
            return len(keys)
        
        return 0
    
    def clear_all(self) -> None:
        """Clear all query caches"""
        cache.clear()
        logger.debug("[QueryCache] CLEAR ALL")


class SessionCache:
    """
    Session data caching pattern
    Store and manage user session data in Redis
    """
    
    def __init__(self, default_ttl: int = 86400):
        """
        Initialize session cache (default 24 hours)
        
        :param default_ttl: Default session TTL in seconds
        """
        self.default_ttl = default_ttl
    
    def set(
        self,
        session_id: str,
        data: dict,
        ttl: Optional[int] = None
    ) -> None:
        """
        Create or update session
        
        :param session_id: Session identifier
        :param data: Session data dictionary
        :param ttl: Optional custom TTL
        """
        key = f"session:{session_id}"
        ttl = ttl or self.default_ttl
        cache.set(key, data, ttl)
        logger.debug(f"[SessionCache] SET: {session_id} (TTL: {ttl}s)")
    
    def get(self, session_id: str) -> Optional[dict]:
        """
        Get session data
        
        :param session_id: Session identifier
        :return: Session data or None if expired/not found
        """
        key = f"session:{session_id}"
        return cache.get(key)
    
    def delete(self, session_id: str) -> None:
        """
        Delete session
        
        :param session_id: Session identifier
        """
        key = f"session:{session_id}"
        cache.delete(key)
        logger.debug(f"[SessionCache] DELETE: {session_id}")
    
    def extend(self, session_id: str, ttl: Optional[int] = None) -> None:
        """
        Extend session TTL (use on activity)
        
        :param session_id: Session identifier
        :param ttl: Optional custom TTL
        """
        key = f"session:{session_id}"
        data = cache.get(key)
        if data:
            ttl = ttl or self.default_ttl
            cache.set(key, data, ttl)
            logger.debug(f"[SessionCache] EXTEND: {session_id} (TTL: {ttl}s)")
    
    def exists(self, session_id: str) -> bool:
        """Check if session exists"""
        return cache.get(f"session:{session_id}") is not None


class RateLimiter:
    """
    Rate limiting pattern (token bucket algorithm)
    Limit requests per time window
    """
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter
        
        :param max_requests: Max requests allowed in window
        :param window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
    
    def is_allowed(self, identifier: str) -> bool:
        """
        Check if request is allowed for identifier
        
        :param identifier: User ID, IP address, or API key
        :return: True if allowed, False if rate limited
        """
        redis_conn = get_redis_connection('default')
        key = f"ratelimit:{identifier}"
        
        current = redis_conn.incr(key)
        
        if current == 1:
            # First request in window, set expiry
            redis_conn.expire(key, self.window_seconds)
        
        allowed = current <= self.max_requests
        
        if not allowed:
            logger.warning(f"[RateLimiter] DENIED: {identifier} ({current}/{self.max_requests})")
        
        return allowed
    
    def get_count(self, identifier: str) -> int:
        """Get current request count"""
        redis_conn = get_redis_connection('default')
        key = f"ratelimit:{identifier}"
        count = redis_conn.get(key)
        return int(count) if count else 0
    
    def get_remaining(self, identifier: str) -> int:
        """Get remaining requests"""
        count = self.get_count(identifier)
        return max(0, self.max_requests - count)
    
    def reset(self, identifier: str) -> None:
        """Reset counter for identifier"""
        redis_conn = get_redis_connection('default')
        key = f"ratelimit:{identifier}"
        redis_conn.delete(key)
        logger.debug(f"[RateLimiter] RESET: {identifier}")


class Leaderboard:
    """
    Leaderboard pattern (sorted sets)
    Manage rankings and scores
    """
    
    def __init__(self, board_name: str = 'default'):
        """
        Initialize leaderboard
        
        :param board_name: Name of the leaderboard
        """
        self.board_name = f"leaderboard:{board_name}"
    
    def set_score(self, member_id: str, score: float) -> None:
        """
        Add or update score for member
        
        :param member_id: Member identifier
        :param score: Score value
        """
        redis_conn = get_redis_connection('default')
        redis_conn.zadd(self.board_name, {member_id: score})
        logger.debug(f"[Leaderboard] SET_SCORE: {member_id} = {score}")
    
    def get_top(self, limit: int = 10) -> List[tuple]:
        """
        Get top N members with scores
        
        :param limit: Number of top members to return
        :return: List of (member_id, score) tuples
        """
        redis_conn = get_redis_connection('default')
        results = redis_conn.zrevrange(
            self.board_name,
            0,
            limit - 1,
            withscores=True
        )
        
        return [
            (
                member.decode() if isinstance(member, bytes) else member,
                int(score) if score.is_integer() else score
            )
            for member, score in results
        ]
    
    def get_rank(self, member_id: str) -> Optional[int]:
        """
        Get rank of member (1-based, highest scores first)
        
        :param member_id: Member identifier
        :return: Rank (1-based) or None if not found
        """
        redis_conn = get_redis_connection('default')
        rank = redis_conn.zrevrank(self.board_name, member_id)
        return rank + 1 if rank is not None else None
    
    def get_score(self, member_id: str) -> Optional[float]:
        """
        Get score of member
        
        :param member_id: Member identifier
        :return: Score or None if not found
        """
        redis_conn = get_redis_connection('default')
        score = redis_conn.zscore(self.board_name, member_id)
        return int(score) if score and score.is_integer() else score
    
    def remove(self, member_id: str) -> None:
        """
        Remove member from leaderboard
        
        :param member_id: Member identifier
        """
        redis_conn = get_redis_connection('default')
        redis_conn.zrem(self.board_name, member_id)
        logger.debug(f"[Leaderboard] REMOVE: {member_id}")
    
    def clear(self) -> None:
        """Clear entire leaderboard"""
        redis_conn = get_redis_connection('default')
        redis_conn.delete(self.board_name)
        logger.debug(f"[Leaderboard] CLEAR: {self.board_name}")
    
    def get_member_context(self, member_id: str, context_range: int = 2) -> List[tuple]:
        """
        Get member and surrounding ranks
        
        :param member_id: Member identifier
        :param context_range: How many members above/below to show
        :return: List of (member_id, score, rank) tuples
        """
        rank = self.get_rank(member_id)
        if rank is None:
            return []
        
        start = max(0, rank - context_range - 1)
        end = rank + context_range - 1
        
        redis_conn = get_redis_connection('default')
        results = redis_conn.zrevrange(
            self.board_name,
            start,
            end,
            withscores=True
        )
        
        return [
            (
                member.decode() if isinstance(member, bytes) else member,
                int(score) if score.is_integer() else score,
                start + i + 1  # Actual rank
            )
            for i, (member, score) in enumerate(results)
        ]
    
    def get_count(self) -> int:
        """Get total number of members in leaderboard"""
        redis_conn = get_redis_connection('default')
        return redis_conn.zcard(self.board_name)


class CounterCache:
    """
    Counter pattern for metrics and statistics
    Atomic increment/decrement operations
    """
    
    def __init__(self, prefix: str = 'counter'):
        """
        Initialize counter cache
        
        :param prefix: Prefix for counter keys
        """
        self.prefix = prefix
    
    def increment(self, name: str, delta: int = 1) -> int:
        """
        Increment counter
        
        :param name: Counter name
        :param delta: Amount to increment
        :return: New counter value
        """
        redis_conn = get_redis_connection('default')
        key = f"{self.prefix}:{name}"
        return redis_conn.incrby(key, delta)
    
    def decrement(self, name: str, delta: int = 1) -> int:
        """Decrement counter"""
        return self.increment(name, -delta)
    
    def get(self, name: str) -> int:
        """Get counter value"""
        redis_conn = get_redis_connection('default')
        key = f"{self.prefix}:{name}"
        value = redis_conn.get(key)
        return int(value) if value else 0
    
    def reset(self, name: str) -> None:
        """Reset counter to zero"""
        redis_conn = get_redis_connection('default')
        key = f"{self.prefix}:{name}"
        redis_conn.delete(key)
    
    def get_all(self) -> dict:
        """Get all counters with this prefix"""
        redis_conn = get_redis_connection('default')
        pattern = f"{self.prefix}:*"
        keys = redis_conn.keys(pattern)
        
        result = {}
        for key in keys:
            key_str = key.decode() if isinstance(key, bytes) else key
            name = key_str.replace(f"{self.prefix}:", "")
            value = redis_conn.get(key)
            result[name] = int(value) if value else 0
        
        return result
