const express = require('express');
const config = require('./config/environment');
const db = require('./config/database');
const checkoutRoutes = require('./routes/checkoutRoutes');
const reportRoutes = require('./routes/reportRoutes');
const userRoutes = require('./routes/userRoutes');
const errorHandler = require('./middlewares/errorHandler');

const app = express();
app.use(express.json());

// Registro de rotas em /api
app.use('/api', checkoutRoutes);
app.use('/api', reportRoutes);
app.use('/api', userRoutes);

// Middleware global de tratamento de erros
app.use(errorHandler);

// Inicialização assíncrona do banco e servidor
async function bootstrap() {
    try {
        await db.init();
        const server = app.listen(config.port, () => {
            console.log(`LMS API refatorada rodando na porta ${config.port} (${config.env})...`);
        });
        return { app, server };
    } catch (err) {
        console.error("Falha ao inicializar o banco de dados:", err);
        process.exit(1);
    }
}

if (require.main === module) {
    bootstrap();
}

module.exports = { app, bootstrap };
