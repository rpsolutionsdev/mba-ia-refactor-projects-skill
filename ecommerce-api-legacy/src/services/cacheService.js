class CacheService {
    constructor() {
        this.cache = new Map();
    }

    set(key, data) {
        console.log(`[CACHE] Salvando chave: ${key}`);
        this.cache.set(key, data);
    }

    get(key) {
        return this.cache.get(key);
    }

    has(key) {
        return this.cache.has(key);
    }

    clear() {
        this.cache.clear();
    }
}

const cacheInstance = new CacheService();
module.exports = cacheInstance;
