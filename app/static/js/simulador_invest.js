// Simulador de Juros Compostos
const form = document.getElementById('simuladorForm');
const resultadoArea = document.getElementById('resultadoArea');
let meuGrafico = null; // inicializa variável global do gráfico

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

    // --- Cálculo do montante final ---
    let montanteFinal = starting_capital;
    let totalAportes = starting_capital;
    let aporteAtual = contribution;

    for (let i = 1; i <= target_time; i++) {
        for (let m = 1; m <= 12; m++) {
            montanteFinal += aporteAtual;
            totalAportes += aporteAtual;
        }
        montanteFinal *= (1 + annual_tax);
        aporteAtual *= (1 + contribution_tax);
    }

    // --- Exibir resultados gerais ---
    document.getElementById('valorInvestido').textContent =
        totalAportes.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

    const totalJuros = montanteFinal - totalAportes;

    document.getElementById('montanteFinal').textContent =
        montanteFinal.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

    document.getElementById('totalJuros').textContent =
        totalJuros.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

    const rendaMensal = montanteFinal * 0.01; // 1% mensal
    document.getElementById('rendaMensal').textContent =
        rendaMensal.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

    resultadoArea.style.display = 'block';

    // --- Arrays para evolução anual ---
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

        anos.push(i);
        montantes.push(montanteAno.toFixed(2));
    }

    // --- Configurar gráfico responsivo ---
    const graficoInvestimentoCtx = document.getElementById('graficoInvestimento').getContext('2d');

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
            responsive: true,           // deixa o gráfico responsivo
            maintainAspectRatio: false, // altura se ajusta ao container
            scales: {
                y: {
                    ticks: {
                        callback: function (value) {
                            return Number(value).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
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

    // --- Preencher tabela mês a mês ---
    const tabelaBody = document.querySelector('#tabelaEvolucao tbody');
    tabelaBody.innerHTML = ''; // limpa tabela antiga

    let aporteMesAtual = contribution;
    let montanteMesAtual = starting_capital;
    let mesNumero = 1;

    for (let i = 1; i <= target_time; i++) {
        for (let m = 1; m <= 12; m++) {
            montanteMesAtual += aporteMesAtual;
            const rendaMensalMes = montanteMesAtual * 0.01;

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${mesNumero}</td>
                <td>${montanteMesAtual.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</td>
                <td>${aporteMesAtual.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</td>
                <td>${rendaMensalMes.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}</td>
            `;
            tabelaBody.appendChild(tr);
            mesNumero++;
        }

        montanteMesAtual *= (1 + annual_tax);
        aporteMesAtual *= (1 + contribution_tax);
    }
});
