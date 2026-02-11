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

    if (target_time <= 0) { alert('Período deve ser maior que zero'); return; }

    let montanteFinal = starting_capital;
    let totalAportes = starting_capital;
    let aporteAtual = contribution;

    for (let i = 1; i <= target_time; i++) {
        for (let m = 1; m <= 12; m++) {
            montanteFinal += aporteAtual;
        }
        montanteFinal *= (1 + annual_tax);
        aporteAtual *= (1 + contribution_tax);
        totalAportes += aporteAtual * 12;
    }

    const totalJuros = montanteFinal - totalAportes;

    document.getElementById('montanteFinal').textContent =
        montanteFinal.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

    document.getElementById('totalJuros').textContent =
        totalJuros.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

    // NOVO: renda mensal aproximada (1%)
    const rendaMensal = montanteFinal * 0.01;
    document.getElementById('rendaMensal').textContent =
        rendaMensal.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });

    resultadoArea.style.display = 'block';

});
