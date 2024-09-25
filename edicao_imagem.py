from PIL import Image, ImageFilter

def editar_imagem(caminho_imagem):
    # Abre a imagem
    imagem = Image.open(caminho_imagem)

    # Converte a imagem para RGB se for uma imagem com paleta
    if imagem.mode == 'P':
        imagem = imagem.convert('RGB')

    # Aplica um filtro de desfoque
    imagem_desfocada = imagem.filter(ImageFilter.BLUR)

    # Aplica um filtro de detalhe
    imagem_detalhe = imagem.filter(ImageFilter.DETAIL)

    # Aplica um filtro nítido
    imagem_nitida = imagem.filter(ImageFilter.SHARPEN)

    # Aplica um filtro de contorno
    imagem_contorno = imagem.filter(ImageFilter.FIND_EDGES)

    # Salva as imagens processadas
    imagem_desfocada.save('imagem_desfocada.png')
    imagem_detalhe.save('imagem_detalhe.png')
    imagem_nitida.save('imagem_nitida.png')
    imagem_contorno.save('imagem_contorno.png')

    # Exibe a imagem original e as processadas
    imagem.show()
    imagem_desfocada.show()
    imagem_detalhe.show()
    imagem_nitida.show()
    imagem_contorno.show()

if __name__ == "__main__":
    # Coloque o caminho da sua imagem aqui
    caminho = './Imagens/ufrn-logo.png'  # Use o caminho correto
    editar_imagem(caminho)
