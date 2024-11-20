from machine import Pin, ADC
import time
import urequests
import network

# Configuração do Wi-Fi
SSID = "DRIA MATOS"
SENHA = "88704551"

# Chave de escrita do ThingSpeak
THINGSPEAK_API_KEY = "HMKHTTW671A7XGZE"  # Insira sua chave de escrita do ThingSpeak aqui

# Função para conectar ao Wi-Fi
def conecta_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(SSID, SENHA)
    while not wifi.isconnected():
        print("Conectando ao Wi-Fi...")
        time.sleep(1)
    print("Conectado ao Wi-Fi:", wifi.ifconfig())

# Conecta ao Wi-Fi
conecta_wifi()

# Configuração dos pinos do ESP32
pino_analogico = ADC(Pin(34))
pino_digital = Pin(25, Pin.IN)
rele = Pin(26, Pin.OUT)

# Configuração do ADC
pino_analogico.atten(ADC.ATTN_11DB)
pino_analogico.width(ADC.WIDTH_12BIT)

# Variáveis para monitorar o estado do sensor
estado_sensor = 0
ultimo_est_sensor = 0

# Limites e margem para controle do relé
UMIDADE_LIMITE = 30
HISTERESE = 5

def mapear(valor, valor_min, valor_max, novo_min, novo_max):
    """Função para mapear o valor de um intervalo para outro"""
    return int((valor - valor_min) * (novo_max - novo_min) / (valor_max - valor_min) + novo_min)

while True:
    # Lê o estado do sensor digital (seco ou molhado)
    estado_sensor = pino_digital.value()

    if estado_sensor == 1 and ultimo_est_sensor == 0:
        print("Umidade Baixa: Irrigando a Planta")
        ultimo_est_sensor = 1
    elif estado_sensor == 0:
        ultimo_est_sensor = 0

    # Lê o valor analógico do sensor de umidade e converte para porcentagem
    val_analog_in = pino_analogico.read()
    porcentagem = mapear(val_analog_in, 0, 4095, 0, 100)

    # Exibe apenas a porcentagem de umidade
    print("Umidade:", porcentagem, "%")

    # Define a ação com base na umidade e no estado do relé
    if porcentagem <= UMIDADE_LIMITE - HISTERESE:
        acao = "Irrigando Planta"
        rele.value(0)
    elif porcentagem >= UMIDADE_LIMITE + HISTERESE:
        acao = "Planta Irrigada"
        rele.value(1)
    else:
        acao = "Monitorando"

    print("Ação:", acao)

    # Envia os dados para o ThingSpeak
    try:
        # Monta a URL manualmente, com a chave de API e o campo de umidade
        url = f"https://api.thingspeak.com/update?api_key={THINGSPEAK_API_KEY}&field1={porcentagem}"

        # Faz a requisição para ThingSpeak
        resposta = urequests.get(url)
        print("Dados enviados ao ThingSpeak:", resposta.text)
        resposta.close()
    except Exception as e:
        print("Erro ao enviar dados para o ThingSpeak:", e)

    time.sleep(10)  # Aguarda 10 segundos antes do próximo ciclo