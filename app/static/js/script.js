const chartElement = document.getElementById('expenseRevenueChart');

if (chartElement) {
    const ctx = chartElement.getContext('2d');

    const expenseRevenueChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 206, 86, 1)',
                    'rgba(75, 192, 192, 1)',
                    'rgba(153, 102, 255, 1)',
                    'rgba(255, 159, 64, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    top: window.innerWidth < 768 ? 5 : 5, // espaço entre topo do canvas e gráfico
                    bottom: 20
                }
            },
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: document.body.classList.contains('dark-mode') ? '#333' : '#fff',
                        font: {
                            size: window.innerWidth >= 768 ? 14 : 12
                        }
                    }
                },
                title: {
                    display: true,
                    text: 'Proporção de Receitas e Tipos de Despesas',
                    font: {
                        size: window.innerWidth < 768 ? 12 : 20,
                        weight: 'bold'
                    },
                    padding: {
                        bottom: window.innerWidth < 768 ? 15 : 30 // distância entre título e gráfico
                    },
                    color: document.body.classList.contains('dark-mode') ? '#333' : '#fff',
                },
                tooltip: {
                    callbacks: {
                        label: function (tooltipItem) {
                            const total = data.reduce((acc, value) => acc + value, 0);
                            const value = tooltipItem.raw;
                            const percentage = ((value / total) * 100).toFixed(2);
                            // Exemplo de if/else se quiser diferenciar tooltips
                            if (tooltipItem.label === "REVENUE_S") {
                                return `💰 : R$${value} (${percentage}%)`;
                            } else {
                                return `📉 : R$${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            },
            cutout: '40%' // tamanho do Doughnut
        }
    });
}

// Configuração modo escuro
// Evento de carregamento de página para configurar o modo escuro
document.addEventListener('DOMContentLoaded', function () {
    // Seleciona os elementos necessários para o modo escuro
    const toggleButton = document.getElementById('dark-mode-toggle');
    const body = document.body;
    const container = document.querySelector('.container');
    const header = document.querySelector('.header');
    const navLinks = document.querySelectorAll('.nav-link');
    const buttons = document.querySelectorAll('button');
    const inputs = document.querySelectorAll('input, select');
    const tables = document.querySelectorAll('table, th, td');
    const footer = document.querySelector('footer');

    // Função para alternar o modo escuro
    function toggleDarkMode() {
        // Alterna a classe 'dark-mode' nos elementos selecionados
        body.classList.toggle('dark-mode');
        container.classList.toggle('dark-mode');
        header.classList.toggle('dark-mode');
        footer.classList.toggle('dark-mode');

        // Alterna a classe 'dark-mode' nos links de navegação
        navLinks.forEach(link => link.classList.toggle('dark-mode'));
        // Alterna a classe 'dark-mode' nos botões
        buttons.forEach(button => button.classList.toggle('dark-mode'));
        // Alterna a classe 'dark-mode' nos inputs
        inputs.forEach(input => input.classList.toggle('dark-mode'));
        // Alterna a classe 'dark-mode' nas tabelas
        tables.forEach(table => table.classList.toggle('dark-mode'));

        // Salva a preferência no localStorage
        if (body.classList.contains('dark-mode')) {
            localStorage.setItem('dark-mode', 'enabled');
        } else {
            localStorage.removeItem('dark-mode');
        }
    }

    // Verifica se a preferência do modo escuro está salva no localStorage
    if (localStorage.getItem('dark-mode') === 'enabled') {
        // Alterna o modo escuro se a preferência estiver salva
        toggleDarkMode();
    }

    // Adiciona o evento de clique ao botão de alternância do modo escuro
    toggleButton.addEventListener('click', toggleDarkMode);
});

document.addEventListener('DOMContentLoaded', function () {
    const startTourBtn = document.getElementById('startTourBtn');

    startTourBtn.addEventListener('click', function () {
        introJs().setOptions({
            nextLabel: 'Próximo',
            prevLabel: 'Anterior',
            skipLabel: 'Pular',
            doneLabel: 'Concluído',
            showProgress: true,
            showBullets: true,
        }).start();
    });
});


document.addEventListener('DOMContentLoaded', function () {
    var calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;

    // Recupera estado riscado do localStorage
    let crossedEvents = JSON.parse(localStorage.getItem('crossedEvents') || '{}');

    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        events: '/api/events',
        height: 'auto',

        // Renderizar título com riscado se estiver marcado
        eventContent: function (info) {
            let id = info.event.id || info.event.startStr + info.event.title; // fallback se não tiver id
            let title = info.event.title;

            if (crossedEvents[id]) {
                title = `<span style="text-decoration: line-through; opacity:0.5;">${title}</span>`;
            }
            return { html: title };
        },

        // Clicar para riscar/desriscar despesas
        eventClick: function (info) {
            if (info.event.backgroundColor === 'red') { // apenas despesas
                let id = info.event.id || info.event.startStr + info.event.title;
                crossedEvents[id] = !crossedEvents[id]; // alterna
                localStorage.setItem('crossedEvents', JSON.stringify(crossedEvents));
                info.event.setProp('title', info.event.title); // força re-render
            }
        }
    });

    calendar.render();
});


document.addEventListener('DOMContentLoaded', function () {
    function startTour() {

        const tour = introJs();

        tour.setOptions({
            nextLabel: 'Próximo',
            prevLabel: 'Voltar',
            doneLabel: 'Concluir',
            skipLabel: 'Pular',
            showProgress: true,
            scrollToElement: true,
            scrollPadding: 80,
            exitOnOverlayClick: false,
            disableInteraction: false,
            showBullets: false,
            steps: [

                {
                    title: "👋 Bem-vindo ao MyFinances",
                    intro: "Vou te mostrar rapidinho como organizar sua vida financeira de forma simples e inteligente."
                },

                {
                    element: document.querySelector('#nav-dashboard'),
                    title: "📊 Dashboard",
                    intro: "Aqui você acompanha sua visão geral financeira."
                },

                {
                    element: document.querySelector('#expense-section'),
                    title: "💸 Cadastro de Despesas",
                    intro: "Registre aqui TODOS os seus gastos. Até o cafézinho hein! Caso não exista o tipo de despesa que deseja, cadastre em Tipos de Transações."
                },

                {
                    element: document.querySelector('#revenue-section'),
                    title: "💰 Cadastro de Receitas",
                    intro: "Adicione suas entradas de dinheiro. Caso não exista o tipo de receita que deseja, cadastre em Tipos de Transações."
                },

                {
                    element: document.querySelector('#wallet-section'),
                    title: "📈 Resumo Financeiro",
                    intro: "Veja seu saldo total e acompanhe sua evolução. Simule corte nos gasto clicando no tipo de despesa na legenda."
                },

                {
                    element: document.querySelector('#chart-section'),
                    title: "📊 Visualização Gráfica",
                    intro: "Analise seus dados com gráficos interativos."
                },

                {
                    element: document.querySelector('#nav-logout'),
                    title: "🚪 Encerrar Sessão",
                    intro: "Passeie, Simule, Apague e refaça quantas vezes quiser. Veja onde seu dinheiro está indo e tome decisões. Boa jornada!"
                }

            ]
        });

        // Scroll suave manual (fica muito mais elegante)
        tour.onbeforechange(function(targetElement) {
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: "smooth",
                    block: "center"
                });
            }
        });

        tour.start();
    }

    // MODO TESTE — sempre inicia
    window.addEventListener("load", function() {
        setTimeout(() => {
            startTour();
        }, 500);
    });
});
