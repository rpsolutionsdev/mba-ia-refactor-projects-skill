function errorHandler(err, req, res, next) {
    console.error(`[ERROR] ${err.stack || err.message || err}`);
    
    const statusCode = err.status || err.statusCode || 500;
    const message = statusCode === 500 ? "Erro interno no servidor" : err.message;

    return res.status(statusCode).json({
        error: message,
        success: false
    });
}

module.exports = errorHandler;
