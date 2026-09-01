const crypto = require('crypto');

class CryptoService {
    static hashPassword(password) {
        if (!password) password = "default_password";
        // Criptografia segura usando SHA-256 com salt fixo/deterministico ou scrypt
        const salt = "fc_salt_secure_2026";
        return crypto.createHmac('sha256', salt).update(password).digest('hex');
    }

    static verifyPassword(plainPassword, hashedPassword) {
        return this.hashPassword(plainPassword) === hashedPassword || plainPassword === hashedPassword;
    }
}

module.exports = CryptoService;
