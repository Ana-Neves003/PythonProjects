import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Carregar dados do arquivo CSV
def load_data(filename):
    return pd.read_csv(filename)

# Limpeza de dados, removendo duplicatas e preenchendo valores ausentes
def clean_data(df):
    df.drop_duplicates(inplace=True)
    df.fillna(method='ffill', inplace=True)  # Preencher valores ausentes
    return df

# Análise Exploratória
def analyze_data(df):
    print("Descrição estatística:\n", df.describe())
    # count: O número total de entradas na coluna
    # mean: A média das vendas
    # std: O desvio padrão
    # min: O valor mínimo na coluna 
    # 25%: O primeiro quartil (Q1), que é o valor abaixo do qual 25% 
    # 50%: O segundo quartil (Q2), que é também a mediana
    # 75%: O terceiro quartil (Q3), que é o valor abaixo do qual 75%
    # max: O valor máximo na coluna
    print("\nContagem de produtos:\n", df['Product'].value_counts())
    #Cálculo da moda
    print("\nModa das Vendas:", df['Sales'].mode()[0])

# Visualização dos gráficos
def visualize_data(df):
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Product', y='Sales', data=df)
    plt.title('Vendas por Produto')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Função principal
def main():
    filename = './Arquivo/sales_data.csv'  
    df = load_data(filename)
    df = clean_data(df)
    analyze_data(df)
    visualize_data(df)

if __name__ == "__main__":
    main()
