// ===============================
// SIMULADOR PROFISSIONAL OTIMIZADO
// ===============================

const form = document.getElementById('simuladorForm');
const resultadoArea = document.getElementById('resultadoArea');
let meuGrafico = null;

form.addEventListener('submit', function (e) {
    e.preventDefault();

    const starting_capital = parseFloat(document.getElementById('starting_capital').value) || 0;
    const contribution = parseFloat(document.getElementById('contribution').value) || 0;
    const contribution_tax = (parseFloat(document.getElementById('contribution_tax').value) || 0) / 100;
    const annual_tax = (parseFloat(document.getElementById('taxaJuros').value) || 0) / 100;
    const years = parseInt(document.getElementById('periodo').value);

    if (years <= 0) {
        alert('Período deve ser maior que zero');
        return;
    }

    const monthly_tax = Math.pow(1 + annual_tax, 1 / 12) - 1;
    const totalMonths = years * 12;

    let montante = starting_capital;
    let aporteAtual = contribution;
    let totalAportes = starting_capital;

    let dadosMensais = [];
    let dadosAnuais = [];

    for (let mes = 1; mes <= totalMonths; mes++) {

        // aplica juros
        montante *= (1 + monthly_tax);

        // adiciona aporte
        montante += aporteAtual;
        totalAportes += aporteAtual;

        // salva dados mensais
        dadosMensais.push({
            mes: mes,
            montante: montante,
            aporte: aporteAtual,
            rendimento: montante * monthly_tax
        });

        // reajusta aporte a cada 12 meses
        if (mes % 12 === 0) {
            dadosAnuais.push({
                ano: mes / 12,
                montante: montante
            });

            aporteAtual *= (1 + contribution_tax);
        }
    }

    const totalJuros = montante - totalAportes;
    const rendaMensal = montante * monthly_tax;

    // ===============================
    // RESULTADOS
    // ===============================

    document.getElementById('valorInvestido').textContent =
        totalAportes.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

    document.getElementById('montanteFinal').textContent =
        montante.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

    document.getElementById('totalJuros').textContent =
        totalJuros.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

    document.getElementById('rendaMensal').textContent =
        rendaMensal.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

    resultadoArea.style.display = 'block';

    // ===============================
    // GRÁFICO (usa dadosAnuais)
    // ===============================

    const ctx = document.getElementById('graficoInvestimento').getContext('2d');

    if (meuGrafico) {
        meuGrafico.destroy();
    }

    meuGrafico = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dadosAnuais.map(d => d.ano),
            datasets: [{
                label: 'Montante ao longo do tempo (R$)',
                data: dadosAnuais.map(d => d.montante),
                fill: true,
                borderColor: '#4fa3f7',
                backgroundColor: 'rgba(79,163,247,0.2)',
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    ticks: {
                        callback: function (value) {
                            return Number(value).toLocaleString('pt-BR', {
                                style: 'currency',
                                currency: 'BRL'
                            });
                        }
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Ano'
                    }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });

    // ===============================
    // TABELA MENSAL (usa dadosMensais)
    // ===============================

    const tabelaBody = document.querySelector('#tabelaEvolucao tbody');
    tabelaBody.innerHTML = '';

    dadosMensais.forEach(d => {
        const tr = document.createElement('tr');

        tr.innerHTML = `
            <td>${d.mes}</td>
            <td>${d.montante.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</td>
            <td>${d.aporte.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</td>
            <td>${d.rendimento.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</td>
        `;

        tabelaBody.appendChild(tr);
    });
});