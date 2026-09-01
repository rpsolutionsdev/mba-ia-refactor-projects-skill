const config = require('../config/environment');

class PaymentService {
    static processPayment(cardNumber, amount) {
        // Mascara o cartão nos logs para segurança
        const maskedCard = cardNumber.length >= 4 
            ? `****-****-****-${cardNumber.slice(-4)}` 
            : '****';

        console.log(`[PAYMENT] Processando transação de R$ ${amount} no cartão ${maskedCard}`);

        // Regra de negócio legada: Cartão iniciando com "4" = PAID, outros = DENIED
        const status = cardNumber.startsWith("4") ? "PAID" : "DENIED";
        return {
            status,
            success: status === "PAID"
        };
    }
}

module.exports = PaymentService;
