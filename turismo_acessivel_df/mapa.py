import folium
import sqlite3

def gerar_mapa():
    conn = sqlite3.connect('acessibilidade_turismo.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT pt.nome, pt.latitude, pt.longitude,
               a.rampa, a.banheiro_adaptado, a.sinalizacao_visual, a.audiodescricao
        FROM ponto_turistico pt
        JOIN acessibilidade a ON pt.id = a.ponto_id
    ''')

    pontos = cursor.fetchall()
    mapa = folium.Map(location=[-15.793889, -47.882778], zoom_start=12)

    for nome, lat, lon, rampa, banheiro, sinal, audio in pontos:
        status = "Acessível"
        cor = "green"
        if not any([rampa, banheiro, sinal, audio]):
            status = "Não Acessível"
            cor = "red"
        elif not all([rampa, banheiro, sinal, audio]):
            status = "Parcialmente Acessível"
            cor = "orange"

        folium.Marker(
            [lat, lon],
            popup=f"<b>{nome}</b><br>Status: {status}",
            icon=folium.Icon(color=cor)
        ).add_to(mapa)

    mapa.save("mapa_turismo.html")
    print("Mapa gerado com sucesso!")

if __name__ == "__main__":
    gerar_mapa()
