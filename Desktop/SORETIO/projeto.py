from flask import Flask, request, jsonify, render_template_string
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import logging
import math

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Google Sheets configuration
CONFIG = {
    'SERVICE_ACCOUNT_FILE': "C:\\Users\\gleysson.ricardo.FASEM\\Desktop\\SORETIO\\composite-rhino-459922-u9-992bc9976840.json",
    'SPREADSHEET_ID': "1gvPQhoZu7_Ln2rh22GiSvdWswVtswRYpC3gVFxmYtfU",
    'SHEET_NAME': 'Página1',
    'SCOPES': ['https://www.googleapis.com/auth/spreadsheets']
}


def get_google_sheets_service():
    """Create and return Google Sheets service"""
    try:
        creds = Credentials.from_service_account_file(
            CONFIG['SERVICE_ACCOUNT_FILE'],
            scopes=CONFIG['SCOPES']
        )
        return build('sheets', 'v4', credentials=creds)
    except Exception as e:
        logger.error(f"Error connecting to Google Sheets: {str(e)}")
        return None


def get_participants_data(service):
    """Get participants and winners data from sheet"""
    try:
        sheet = service.spreadsheets()

        # Get participants (column A)
        result = sheet.values().get(
            spreadsheetId=CONFIG['SPREADSHEET_ID'],
            range=f"{CONFIG['SHEET_NAME']}!A2:A"
        ).execute()
        values = result.get('values', [])
        names = [row[0] for row in values if row and row[0].strip()]

        # Get winners (column B)
        result_winners = sheet.values().get(
            spreadsheetId=CONFIG['SPREADSHEET_ID'],
            range=f"{CONFIG['SHEET_NAME']}!B2:B"
        ).execute()
        winners_values = result_winners.get('values', [])

        # Process data
        winners = []
        remaining_names = []

        for i, name in enumerate(names):
            if i < len(winners_values) and winners_values[i] and winners_values[i][0].strip().upper() == 'GANHADOR':
                winners.append(name)
            else:
                remaining_names.append(name)

        return remaining_names, winners

    except Exception as e:
        logger.error(f"Error getting sheet data: {str(e)}")
        raise


@app.route('/')
def index():
    """Main route showing the raffle wheel"""
    try:
        service = get_google_sheets_service()
        if not service:
            return "Google Sheets connection error", 500

        names, winners = get_participants_data(service)
        return render_template_string(
            HTML_TEMPLATE,
            nomes=names,
            ganhadores=winners
        )

    except Exception as e:
        logger.error(f"Main route error: {str(e)}")
        return "Error loading page", 500


@app.route('/marcar_ganhador', methods=['POST'])
def mark_winner():
    """Mark a winner in the spreadsheet"""
    try:
        data = request.get_json()
        if not data or 'nome' not in data:
            logger.warning("Invalid request data")
            return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

        name = data['nome']
        service = get_google_sheets_service()
        if not service:
            return jsonify({'status': 'error', 'message': 'Google Sheets connection error'}), 500

        sheet = service.spreadsheets()

        # Find name row in column A
        result = sheet.values().get(
            spreadsheetId=CONFIG['SPREADSHEET_ID'],
            range=f"{CONFIG['SHEET_NAME']}!A2:A"
        ).execute()
        values = result.get('values', [])
        names = [row[0] for row in values if row and row[0].strip()]

        if name not in names:
            logger.warning(f"Name not found: {name}")
            return jsonify({'status': 'error', 'message': 'Name not found'}), 404

        row_index = names.index(name) + 2  # +2 because sheet starts at row 2

        # Update corresponding cell in column B
        sheet.values().update(
            spreadsheetId=CONFIG['SPREADSHEET_ID'],
            range=f"{CONFIG['SHEET_NAME']}!B{row_index}",
            valueInputOption='RAW',
            body={'values': [['Ganhador']]}
        ).execute()

        logger.info(f"Winner marked successfully: {name}")
        return jsonify({'status': 'success'})

    except Exception as e:
        logger.error(f"Error marking winner: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Roleta de Sorteio</title>
    <style>
        body {
            font-family: 'Segoe UI', Roboto, sans-serif;
            background: #f5f7fa;
            margin: 0;
            padding: 20px;
            color: #2c3e50;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            padding: 30px;
        }
        h1 {
            color: #3498db;
            text-align: center;
            margin-bottom: 30px;
        }
        #roleta-container {
            position: relative;
            margin: 30px auto;
            width: 100%;
            max-width: 500px;
            aspect-ratio: 1/1;
        }
        #wheel {
            width: 100%;
            height: 100%;
            transform: rotate(0deg);
            transition: transform 5s cubic-bezier(0.17, 0.89, 0.32, 0.98);
            border-radius: 50%;
            box-shadow: 0 0 20px rgba(0,0,0,0.2);
        }
        #marker {
            position: absolute;
            top: -15px;
            left: 50%;
            transform: translateX(-50%);
            width: 40px;
            height: 40px;
            background-color: #e74c3c;
            clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
            z-index: 10;
            filter: drop-shadow(0 0 8px rgba(0,0,0,0.3));
        }
        .button-group {
            display: flex;
            justify-content: center;
            gap: 15px;
            margin: 30px 0;
            flex-wrap: wrap;
        }
        button {
            padding: 12px 24px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
            font-weight: 600;
        }
        button:hover {
            background: #2980b9;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        button:disabled {
            background: #95a5a6;
            cursor: not-allowed;
        }
        #ganhador {
            font-size: 1.5rem;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            background: rgba(46, 204, 113, 0.1);
            border-radius: 8px;
        }
        #ganhadoresLista {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-top: 30px;
            display: none;
        }
        #ganhadoresLista h3 {
            margin-top: 0;
            color: #2c3e50;
        }
        #ganhadoresLista ul {
            list-style: none;
            padding: 0;
        }
        #ganhadoresLista li {
            padding: 10px;
            margin: 5px 0;
            background: white;
            border-radius: 4px;
        }
        @media (max-width: 600px) {
            .container {
                padding: 15px;
            }
            #roleta-container {
                max-width: 300px;
            }
            button {
                padding: 10px 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎡 Roleta de Sorteio 🎡</h1>

        <div id="roleta-container">
            <div id="marker"></div>
            <svg id="wheel" viewBox="0 0 500 500" xmlns="http://www.w3.org/2000/svg"></svg>
        </div>

        <div class="button-group">
            <button id="btnSortear" {{ 'disabled' if nomes|length == 0 }}>Sortear</button>
            <button id="btnMostrarGanhadores">Mostrar Ganhadores</button>
            <button id="btnFecharGanhadores" style="display:none;">Fechar</button>
        </div>

        <div id="ganhador"></div>

        <div id="ganhadoresLista">
            <h3>Ganhadores Anteriores</h3>
            <ul>
                {% for g in ganhadores %}
                    <li>{{ g }}</li>
                {% else %}
                    <li>Nenhum ganhador ainda.</li>
                {% endfor %}
            </ul>
        </div>
    </div>

<script>
    const nomes = {{ nomes|tojson }};
    const ganhadores = {{ ganhadores|tojson }};
    const wheel = document.getElementById('wheel');
    const marker = document.getElementById('marker');
    const btnSortear = document.getElementById('btnSortear');
    const btnMostrarGanhadores = document.getElementById('btnMostrarGanhadores');
    const btnFecharGanhadores = document.getElementById('btnFecharGanhadores');
    const ganhadorDiv = document.getElementById('ganhador');
    const ganhadoresLista = document.getElementById('ganhadoresLista');

    const colors = ['#e74c3c', '#3498db', '#f1c40f', '#9b59b6', '#2ecc71', '#e67e22', '#1abc9c', '#34495e'];
    const radius = 250;
    const center = 250;
    let currentRotation = 0;

    function createSegmentPath(startAngle, endAngle) {
        const startRad = (startAngle - 90) * Math.PI / 180;
        const endRad = (endAngle - 90) * Math.PI / 180;

        const x1 = center + radius * Math.cos(startRad);
        const y1 = center + radius * Math.sin(startRad);
        const x2 = center + radius * Math.cos(endRad);
        const y2 = center + radius * Math.sin(endRad);

        const largeArc = (endAngle - startAngle) > 180 ? 1 : 0;

        return `M${center},${center} L${x1},${y1} A${radius},${radius} 0 ${largeArc} 1 ${x2},${y2} Z`;
    }

    function desenharRoleta() {
        wheel.innerHTML = '';
        const num = nomes.length;
        if (num === 0) return;

        const segmentAngle = 360 / num;

        nomes.forEach((nome, i) => {
            const startAngle = i * segmentAngle;
            const endAngle = startAngle + segmentAngle;
            const midAngle = startAngle + segmentAngle / 2;

            // Create segment
            const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
            path.setAttribute('d', createSegmentPath(startAngle, endAngle));
            path.setAttribute('fill', colors[i % colors.length]);
            path.setAttribute('stroke', '#fff');
            path.setAttribute('stroke-width', '2');
            wheel.appendChild(path);

            // Calculate text position - improved alignment
            const textRadius = radius * 0.65;
            const textAngleRad = (midAngle - 90) * Math.PI / 180;
            const x = center + textRadius * Math.cos(textAngleRad);
            const y = center + textRadius * Math.sin(textAngleRad);

            // Adjust rotation for readability
            let textRotation = midAngle;
            if (midAngle > 90 && midAngle < 270) {
                textRotation += 180;
            }

            // Create text element
            const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
            text.setAttribute('x', x);
            text.setAttribute('y', y);
            text.setAttribute('fill', 'white');
            text.setAttribute('font-size', Math.min(14, segmentAngle / 3));
            text.setAttribute('font-weight', 'bold');
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('dominant-baseline', 'middle');
            text.setAttribute('transform', `rotate(${textRotation},${x},${y})`);
            text.style.userSelect = 'none';

            // Truncate text if needed
            const maxChars = Math.max(3, Math.floor(segmentAngle / 5));
            text.textContent = nome.length > maxChars ? nome.substring(0, maxChars-3) + '...' : nome;

            wheel.appendChild(text);
        });
    }

    function girarRoleta() {
        if (girando || nomes.length === 0) return;

        girando = true;
        btnSortear.disabled = true;
        ganhadorDiv.textContent = '';

        const spins = 5;
        const segmentAngle = 360 / nomes.length;
        const winnerIndex = Math.floor(Math.random() * nomes.length);

        // Calculate stop position (clockwise)
        const stopAngle = currentRotation + 360 * spins + (360 - (winnerIndex * segmentAngle + segmentAngle / 2));
        currentRotation = stopAngle % 360;

        wheel.style.transition = 'transform 6s cubic-bezier(0.17, 0.89, 0.32, 0.98)';
        wheel.style.transform = `rotate(${stopAngle}deg)`;

        wheel.addEventListener('transitionend', function handler() {
            wheel.style.transition = 'none';
            wheel.style.transform = `rotate(${currentRotation}deg)`;

            girando = false;
            btnSortear.disabled = nomes.length === 0;

            const winner = nomes[winnerIndex];
            ganhadorDiv.textContent = `🎉 Ganhador: ${winner} 🎉`;

            fetch('/marcar_ganhador', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({nome: winner})
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    nomes.splice(winnerIndex, 1);
                    ganhadores.push(winner);
                    desenharRoleta();
                    atualizarListaGanhadores();
                } else {
                    throw new Error(data.message || 'Unknown error');
                }
            })
            .catch(error => {
                alert('Erro: ' + error.message);
            });

            wheel.removeEventListener('transitionend', handler);
        }, {once: true});
    }

    function atualizarListaGanhadores() {
        const ul = ganhadoresLista.querySelector('ul');
        ul.innerHTML = ganhadores.length === 0
            ? '<li>Nenhum ganhador ainda.</li>'
            : ganhadores.map(g => `<li>${g}</li>`).join('');
    }

    // Event listeners
    btnSortear.addEventListener('click', girarRoleta);

    btnMostrarGanhadores.addEventListener('click', () => {
        ganhadoresLista.style.display = 'block';
        btnMostrarGanhadores.style.display = 'none';
        btnFecharGanhadores.style.display = 'inline-block';
    });

    btnFecharGanhadores.addEventListener('click', () => {
        ganhadoresLista.style.display = 'none';
        btnMostrarGanhadores.style.display = 'inline-block';
        btnFecharGanhadores.style.display = 'none';
    });

    // Initialize
    let girando = false;
    desenharRoleta();
    atualizarListaGanhadores();
</script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
