const CourseModel = require('../models/courseModel');
const UserModel = require('../models/userModel');
const EnrollmentModel = require('../models/enrollmentModel');
const PaymentModel = require('../models/paymentModel');
const PaymentService = require('../services/paymentService');
const CryptoService = require('../services/cryptoService');
const cache = require('../services/cacheService');

class CheckoutController {
    static async processCheckout(req, res, next) {
        try {
            // Suporta tanto os nomes originais de campos quanto nomes semânticos
            const username = req.body.usr || req.body.username;
            const email = req.body.eml || req.body.email;
            const password = req.body.pwd || req.body.password || "123456";
            const courseId = req.body.c_id || req.body.courseId;
            const cardNumber = req.body.card || req.body.cardNumber;

            if (!username || !email || !courseId || !cardNumber) {
                return res.status(400).send("Bad Request");
            }

            const course = await CourseModel.findActiveById(courseId);
            if (!course) {
                return res.status(404).send("Curso não encontrado");
            }

            let user = await UserModel.findByEmail(email);
            let userId;

            if (!user) {
                const hashedPassword = CryptoService.hashPassword(password);
                userId = await UserModel.create(username, email, hashedPassword);
            } else {
                userId = user.id;
            }

            // Processamento do pagamento
            const paymentResult = PaymentService.processPayment(cardNumber, course.price);
            if (!paymentResult.success) {
                return res.status(400).send("Pagamento recusado");
            }

            // Criação da matrícula e registro do pagamento
            const enrollmentId = await EnrollmentModel.create(userId, courseId);
            await PaymentModel.create(enrollmentId, course.price, paymentResult.status);
            await PaymentModel.logAudit(`Checkout curso ${courseId} por ${userId}`);

            cache.set(`last_checkout_${userId}`, course.title);

            return res.status(200).json({
                msg: "Sucesso",
                enrollment_id: enrollmentId
            });
        } catch (error) {
            next(error);
        }
    }
}

module.exports = CheckoutController;
