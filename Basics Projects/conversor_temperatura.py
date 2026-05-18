def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5/9

temp = float(input("Digite a temperatura: "))
escolha = input("Converter para (C)elsius ou (F)ahrenheit? ")

if escolha.lower() == 'c':
    print("Temperatura em Celsius:", fahrenheit_to_celsius(temp))
elif escolha.lower() == 'f':
    print("Temperatura em Fahrenheit:", celsius_to_fahrenheit(temp))
else:
    print("Opção inválida!")
