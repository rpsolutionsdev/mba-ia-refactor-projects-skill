const crypto = require('crypto');

class CryptoService {
    /**
     * Gera hash de senha criptograficamente seguro utilizando scrypt nativo do Node.js
     * com salt aleatório exclusivo (16 bytes / 32 hex) gerado individualmente por usuário.
     * Formato retornado: `scrypt:<salt>:<derivedKey>`
     */
    static hashPassword(password) {
        if (!password) password = "default_password";
        // Salt criptográfico único e imprevisível por usuário
        const salt = crypto.randomBytes(16).toString('hex');
        // Derivação de chave de 64 bytes via scrypt
        const derivedKey = crypto.scryptSync(password, salt, 64).toString('hex');
        return `scrypt:${salt}:${derivedKey}`;
    }

    /**
     * Validação estrita de senha em tempo constante (timingSafeEqual).
     * Extrai o salt único armazenado no registro do usuário.
     * TOLERÂNCIA ZERO para fallbacks inseguros (MD5, base64 ou plaintext).
     */
    static verifyPassword(plainPassword, storedHash) {
        if (!plainPassword || !storedHash) return false;

        const parts = storedHash.split(':');
        // Exige conformidade estrita com o formato seguro scrypt:<salt>:<derivedKey>
        if (parts.length !== 3 || parts[0] !== 'scrypt') {
            return false; // Rejeita imediatamente qualquer formato legado ou adulterado
        }

        const [, salt, originalKeyHex] = parts;
        const keyBuffer = Buffer.from(originalKeyHex, 'hex');
        const derivedKey = crypto.scryptSync(plainPassword, salt, 64);

        if (keyBuffer.length !== derivedKey.length) {
            return false;
        }

        // Comparação segura em tempo constante contra timing attacks
        return crypto.timingSafeEqual(keyBuffer, derivedKey);
    }
}

module.exports = CryptoService;

