import asyncpg
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import config

class Database:
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        """Database bilan ulanish"""
        self.pool = await asyncpg.create_pool(
            config.DATABASE_URL,
            min_size=5,
            max_size=20
        )
    
    async def disconnect(self):
        """Database ulanishini yopish"""
        if self.pool:
            await self.pool.close()
    
    async def create_tables(self):
        """Barcha jadvallarni yaratish"""
        async with self.pool.acquire() as conn:
            # Users jadvali
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username VARCHAR(255),
                    full_name VARCHAR(255),
                    joined_date TIMESTAMP DEFAULT NOW(),
                    is_blocked BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Films jadvali
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS films (
                    id SERIAL PRIMARY KEY,
                    code VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    thumbnail_file_id VARCHAR(255),
                    created_date TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Film parts jadvali
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS film_parts (
                    id SERIAL PRIMARY KEY,
                    film_code VARCHAR(50) REFERENCES films(code) ON DELETE CASCADE,
                    part_number INTEGER NOT NULL,
                    video_file_id VARCHAR(255) NOT NULL,
                    added_date TIMESTAMP DEFAULT NOW(),
                    UNIQUE(film_code, part_number)
                )
            ''')
            
            # Film views jadvali
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS film_views (
                    id SERIAL PRIMARY KEY,
                    film_code VARCHAR(50) REFERENCES films(code) ON DELETE CASCADE,
                    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
                    viewed_date TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Channels jadvali
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS channels (
                    id SERIAL PRIMARY KEY,
                    channel_id BIGINT UNIQUE NOT NULL,
                    channel_username VARCHAR(255),
                    channel_title VARCHAR(255),
                    added_date TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Admins jadvali
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    user_id BIGINT PRIMARY KEY,
                    permissions TEXT[] DEFAULT ARRAY[]::TEXT[],
                    added_by BIGINT,
                    added_date TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Settings jadvali
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key VARCHAR(255) PRIMARY KEY,
                    value TEXT
                )
            ''')
            
            # Admin contact link ni sozlamalarga qo'shish
            await conn.execute('''
                INSERT INTO settings (key, value)
                VALUES ('admin_contact_link', $1)
                ON CONFLICT (key) DO NOTHING
            ''', config.ADMIN_CONTACT_LINK)
    
    # =============== USER METHODS ===============
    
    async def add_user(self, user_id: int, username: str = None, full_name: str = None):
        """Yangi foydalanuvchi qo'shish"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO users (user_id, username, full_name)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO UPDATE
                SET username = $2, full_name = $3
            ''', user_id, username, full_name)
    
    async def get_user(self, user_id: int):
        """Foydalanuvchi ma'lumotlarini olish"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow('SELECT * FROM users WHERE user_id = $1', user_id)
    
    async def get_all_users(self):
        """Barcha foydalanuvchilarni olish"""
        async with self.pool.acquire() as conn:
            return await conn.fetch('SELECT user_id FROM users WHERE is_blocked = FALSE')
    
    async def get_users_count(self):
        """Jami foydalanuvchilar soni"""
        async with self.pool.acquire() as conn:
            return await conn.fetchval('SELECT COUNT(*) FROM users')
    
    async def get_users_by_period(self, days: int):
        """Ma'lum davr ichida qo'shilgan foydalanuvchilar soni"""
        async with self.pool.acquire() as conn:
            date_from = datetime.now() - timedelta(days=days)
            return await conn.fetchval('''
                SELECT COUNT(*) FROM users 
                WHERE joined_date >= $1
            ''', date_from)
    
    async def get_daily_views(self):
        """Kunlik ko'rishlar soni"""
        async with self.pool.acquire() as conn:
            today = datetime.now().date()
            return await conn.fetchval('''
                SELECT COUNT(*) FROM film_views 
                WHERE DATE(viewed_date) = $1
            ''', today)
    
    # =============== FILM METHODS ===============
    
    async def add_film(self, code: str, name: str, description: str, thumbnail_file_id: str):
        """Yangi kino qo'shish"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO films (code, name, description, thumbnail_file_id)
                VALUES ($1, $2, $3, $4)
            ''', code, name, description, thumbnail_file_id)
    
    async def get_film(self, code: str):
        """Kino ma'lumotlarini olish"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow('SELECT * FROM films WHERE code = $1', code)
    
    async def delete_film(self, code: str):
        """Kinoni o'chirish"""
        async with self.pool.acquire() as conn:
            await conn.execute('DELETE FROM films WHERE code = $1', code)
    
    async def get_all_films(self):
        """Barcha kinolarni olish"""
        async with self.pool.acquire() as conn:
            return await conn.fetch('SELECT code, name FROM films ORDER BY created_date DESC')
    
    async def get_films_paginated(self, offset: int = 0, limit: int = 30):
        """Sahifalangan kinolar ro'yxati"""
        async with self.pool.acquire() as conn:
            films = await conn.fetch('''
                SELECT code, name FROM films 
                ORDER BY created_date DESC
                LIMIT $1 OFFSET $2
            ''', limit, offset)
            total = await conn.fetchval('SELECT COUNT(*) FROM films')
            return films, total
    
    # =============== FILM PARTS METHODS ===============
    
    async def add_film_part(self, film_code: str, part_number: int, video_file_id: str):
        """Kino qismi qo'shish"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO film_parts (film_code, part_number, video_file_id)
                VALUES ($1, $2, $3)
            ''', film_code, part_number, video_file_id)
    
    async def get_film_parts(self, film_code: str):
        """Kino qismlarini olish"""
        async with self.pool.acquire() as conn:
            return await conn.fetch('''
                SELECT * FROM film_parts 
                WHERE film_code = $1 
                ORDER BY part_number
            ''', film_code)
    
    async def get_film_part(self, film_code: str, part_number: int):
        """Bitta kino qismini olish"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow('''
                SELECT * FROM film_parts 
                WHERE film_code = $1 AND part_number = $2
            ''', film_code, part_number)
    
    async def delete_film_part(self, film_code: str, part_number: int):
        """Kino qismini o'chirish"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                DELETE FROM film_parts 
                WHERE film_code = $1 AND part_number = $2
            ''', film_code, part_number)
    
    async def get_parts_count(self, film_code: str):
        """Kino qismlari soni"""
        async with self.pool.acquire() as conn:
            return await conn.fetchval('''
                SELECT COUNT(*) FROM film_parts WHERE film_code = $1
            ''', film_code)
    
    # =============== FILM VIEWS METHODS ===============
    
    async def add_film_view(self, film_code: str, user_id: int):
        """Kino ko'rilganini qayd qilish"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO film_views (film_code, user_id)
                VALUES ($1, $2)
            ''', film_code, user_id)
    
    async def get_top_films(self, limit: int = 20):
        """Eng ko'p ko'rilgan kinolar"""
        async with self.pool.acquire() as conn:
            return await conn.fetch('''
                SELECT f.name, f.code, COUNT(fv.id) as views_count
                FROM films f
                LEFT JOIN film_views fv ON f.code = fv.film_code
                GROUP BY f.code, f.name
                ORDER BY views_count DESC
                LIMIT $1
            ''', limit)
    
    # =============== CHANNEL METHODS ===============
    
    async def add_channel(self, channel_id: int, channel_username: str = None, channel_title: str = None):
        """Kanal qo'shish"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO channels (channel_id, channel_username, channel_title)
                VALUES ($1, $2, $3)
                ON CONFLICT (channel_id) DO UPDATE
                SET channel_username = $2, channel_title = $3
            ''', channel_id, channel_username, channel_title)
    
    async def delete_channel(self, channel_id: int):
        """Kanalni o'chirish"""
        async with self.pool.acquire() as conn:
            await conn.execute('DELETE FROM channels WHERE channel_id = $1', channel_id)
    
    async def get_all_channels(self):
        """Barcha kanallarni olish"""
        async with self.pool.acquire() as conn:
            return await conn.fetch('SELECT * FROM channels ORDER BY added_date')
    
    # =============== ADMIN METHODS ===============
    
    async def add_admin(self, user_id: int, permissions: List[str], added_by: int):
        """Admin qo'shish"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO admins (user_id, permissions, added_by)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO UPDATE
                SET permissions = $2
            ''', user_id, permissions, added_by)
    
    async def get_admin(self, user_id: int):
        """Admin ma'lumotlarini olish"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow('SELECT * FROM admins WHERE user_id = $1', user_id)
    
    async def get_all_admins(self):
        """Barcha adminlarni olish"""
        async with self.pool.acquire() as conn:
            return await conn.fetch('SELECT * FROM admins')
    
    async def delete_admin(self, user_id: int):
        """Adminni o'chirish"""
        async with self.pool.acquire() as conn:
            await conn.execute('DELETE FROM admins WHERE user_id = $1', user_id)
    
    async def is_admin(self, user_id: int):
        """Foydalanuvchi admin ekanligini tekshirish"""
        if user_id == config.OWNER_ID:
            return True
        async with self.pool.acquire() as conn:
            result = await conn.fetchval('SELECT COUNT(*) FROM admins WHERE user_id = $1', user_id)
            return result > 0
    
    async def has_permission(self, user_id: int, permission: str):
        """Admin ruxsatini tekshirish"""
        if user_id == config.OWNER_ID:
            return True
        async with self.pool.acquire() as conn:
            permissions = await conn.fetchval('SELECT permissions FROM admins WHERE user_id = $1', user_id)
            if permissions and ('all' in permissions or '7' in permissions or permission in permissions):
                return True
            return False
    
    # =============== SETTINGS METHODS ===============
    
    async def get_setting(self, key: str):
        """Sozlamani olish"""
        async with self.pool.acquire() as conn:
            return await conn.fetchval('SELECT value FROM settings WHERE key = $1', key)
    
    async def set_setting(self, key: str, value: str):
        """Sozlamani o'rnatish"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO settings (key, value)
                VALUES ($1, $2)
                ON CONFLICT (key) DO UPDATE
                SET value = $2
            ''', key, value)


# Global database instance
db = Database()
