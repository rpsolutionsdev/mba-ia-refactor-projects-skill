const { app, bootstrap } = require('./src/app');
const http = require('http');

async function runTests() {
    console.log("--- TESTANDO ENDPOINTS DE ECOMMERCE-API-LEGACY (NODE.JS) ---");
    const { server } = await bootstrap();
    const port = server.address().port;

    const request = (method, path, body = null) => {
        return new Promise((resolve, reject) => {
            const options = {
                hostname: 'localhost',
                port: port,
                path: path,
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                }
            };

            const req = http.request(options, (res) => {
                let data = '';
                res.on('data', chunk => data += chunk);
                res.on('end', () => {
                    resolve({
                        status: res.statusCode,
                        body: data,
                        json: () => {
                            try { return JSON.parse(data); } catch (e) { return data; }
                        }
                    });
                });
            });

            req.on('error', reject);
            if (body) {
                req.write(JSON.stringify(body));
            }
            req.end();
        });
    };

    try {
        // 0. Testes Unitários de Hashing Seguro (CryptoService com scryptSync e Salt Único)
        const CryptoService = require('./src/services/cryptoService');
        const hash1 = CryptoService.hashPassword("senhaforte123");
        const hash2 = CryptoService.hashPassword("senhaforte123");

        if (!hash1.startsWith('scrypt:')) {
            throw new Error(`Hash inválido, deve iniciar com scrypt: : ${hash1}`);
        }
        const parts1 = hash1.split(':');
        const parts2 = hash2.split(':');
        if (parts1.length !== 3 || parts2.length !== 3) {
            throw new Error(`Hash deve conter 3 partes (scrypt:salt:key): ${hash1}`);
        }
        if (parts1[1] === parts2[1]) {
            throw new Error(`Falha de segurança: os salts gerados para o mesmo input devem ser diferentes (únicos por usuário/chamada)! Salt1=${parts1[1]}, Salt2=${parts2[1]}`);
        }
        if (parts1[1] === "fc_salt_secure_2026" || parts2[1] === "fc_salt_secure_2026") {
            throw new Error("Falha de segurança: salt fixo estático detectado!");
        }
        if (!CryptoService.verifyPassword("senhaforte123", hash1)) {
            throw new Error("Falha na validação de senha válida com scrypt");
        }
        if (CryptoService.verifyPassword("senha_incorreta", hash1)) {
            throw new Error("Falha: senha incorreta foi aceita!");
        }
        if (CryptoService.verifyPassword("senhaforte123", "plaintext") || CryptoService.verifyPassword("senhaforte123", "fc_salt_secure_2026")) {
            throw new Error("Falha: fallback para texto puro ou formato inseguro aceito!");
        }
        console.log(`[OK] [CryptoService] scryptSync com salt único por usuário validado: salt=${parts1[1].substring(0, 8)}... (salt único gerado com sucesso)`);

        // 1. Checkout Sucesso
        const res1 = await request('POST', '/api/checkout', {
            usr: "Guilherme",
            eml: "gui@fullcycle.com.br",
            pwd: "senhaforte",
            c_id: 2,
            card: "4111222233334444"
        });
        if (res1.status !== 200) throw new Error(`Checkout sucesso falhou: ${res1.status} - ${res1.body}`);
        const data1 = res1.json();
        console.log(`[OK] [POST /api/checkout] Sucesso: enrollment_id=${data1.enrollment_id}`);

        // 2. Checkout Recusado
        const res2 = await request('POST', '/api/checkout', {
            usr: "João",
            eml: "joao@teste.com",
            pwd: "123",
            c_id: 1,
            card: "5111222233334444"
        });
        if (res2.status !== 400) throw new Error(`Checkout recusado deveria retornar 400, retornou ${res2.status}`);
        console.log(`[OK] [POST /api/checkout] Recusado: status 400 correto`);

        // 3. Relatório Financeiro
        const res3 = await request('GET', '/api/admin/financial-report');
        if (res3.status !== 200) throw new Error(`Relatório falhou: ${res3.status}`);
        const report = res3.json();
        if (!Array.isArray(report) || report.length === 0) throw new Error("Relatório vazio");
        console.log(`[OK] [GET /api/admin/financial-report] Sucesso: ${report.length} cursos listados`);

        // 4. Deletar Usuário
        const res4 = await request('DELETE', '/api/users/1');
        if (res4.status !== 200) throw new Error(`Deletar usuário falhou: ${res4.status}`);
        console.log(`[OK] [DELETE /api/users/1] Sucesso: ${res4.body}`);

        console.log("\nTODOS OS TESTES DO PROJETO 2 PASSARAM COM SUCESSO!");
    } finally {
        server.close();
        process.exit(0);
    }
}

runTests().catch(err => {
    console.error("ERRO NOS TESTES:", err);
    process.exit(1);
});
