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
