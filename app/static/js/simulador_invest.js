// Simulador de Juros Compostos
const form = document.getElementById('simuladorForm');
const resultadoArea = document.getElementById('resultadoArea');

form.addEventListener('submit', function (e) {
    e.preventDefault();

    const starting_capital = parseFloat(document.getElementById('starting_capital').value) || 0;
    const contribution = parseFloat(document.getElementById('contribution').value) || 0;
    const contribution_tax = parseFloat(document.getElementById('contribution_tax').value) / 100 || 0;
    const annual_tax = parseFloat(document.getElementById('taxaJuros').value) / 100 || 0;
    const target_time = parseFloat(document.getElementById('periodo').value);

    if (target_time <= 0) {
        alert('Período deve ser maior que zero');
        return;
    }

    let montanteFinal = starting_capital;
    let totalAportes = starting_capital;
    let aporteAtual = contribution;

    // Calcula mês a mês
    for (let i = 1; i <= target_time; i++) {
        for (let m = 1; m <= 12; m++) {
            montanteFinal += aporteAtual;
            totalAportes += aporteAtual;
        }
        // Aplica juros anuais
        montanteFinal *= (1 + annual_tax);
        // Aumenta o aporte anual conforme a taxa
        aporteAtual *= (1 + contribution_tax);
    }

    const totalJuros = montanteFinal - totalAportes;

    // Exibe resultados formatados em BRL
    document.getElementById('montanteFinal').textContent =
        montanteFinal.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

    document.getElementById('totalJuros').textContent =
        totalJuros.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

    const rendaMensal = montanteFinal * 0.01; // 1% mensal
    document.getElementById('rendaMensal').textContent =
        rendaMensal.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

    resultadoArea.style.display = 'block';

    // Arrays para armazenar evolução ano a ano
    let anos = [];
    let montantes = [];

    let montanteAno = starting_capital;
    let aporteAno = contribution;

    for (let i = 1; i <= target_time; i++) {
        for (let m = 1; m <= 12; m++) {
            montanteAno += aporteAno;
        }
        montanteAno *= (1 + annual_tax);
        aporteAno *= (1 + contribution_tax);

        // Armazena para o gráfico
        anos.push(i);
        montantes.push(montanteAno.toFixed(2));
    }

    // --- Criar o gráfico ---
    let graficoInvestimentoCtx = document.getElementById('graficoInvestimento').getContext('2d');
    if (meuGrafico) {
        meuGrafico.destroy();
    }
    meuGrafico = new Chart(graficoInvestimentoCtx, {
        type: 'line',
        data: {
            labels: anos,
            datasets: [{
                label: 'Montante ao longo do tempo (R$)',
                data: montantes,
                fill: true,
                borderColor: '#4fa3f7',
                backgroundColor: 'rgba(79,163,247,0.2)',
                tension: 0.3
            }]
        },
        options: {
            scales: {
                y: {
                    ticks: {
                        callback: function (value) {
                            return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
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

});

let meuGrafico = null;

