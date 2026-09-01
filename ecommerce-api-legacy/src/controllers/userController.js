const UserModel = require('../models/userModel');

class UserController {
    static async deleteUser(req, res, next) {
        try {
            const { id } = req.params;
            const deleted = await UserModel.delete(id);
            if (!deleted) {
                return res.status(404).send("Usuário não encontrado");
            }
            return res.send("Usuário e registros associados deletados com sucesso.");
        } catch (error) {
            next(error);
        }
    }
}

module.exports = UserController;
