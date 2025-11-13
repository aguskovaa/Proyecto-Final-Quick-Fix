from flask import Flask, render_template, request, jsonify
import mercadopago
import os

app = Flask(__name__)

# Configura tus credenciales de Mercado Pago
MP_ACCESS_TOKEN = "TU_ACCESS_TOKEN_AQUI"  # Reemplaza con tu token
sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_preference', methods=['POST'])
def create_preference():
    try:
        # Datos del producto/pago
        preference_data = {
            "items": [
                {
                    "title": request.json.get('product_name', 'Producto de ejemplo'),
                    "quantity": int(request.json.get('quantity', 1)),
                    "currency_id": "ARS",  # Puedes cambiar la moneda
                    "unit_price": float(request.json.get('price', 100))
                }
            ],
            "back_urls": {
                "success": "http://localhost:5000/success",
                "failure": "http://localhost:5000/failure",
                "pending": "http://localhost:5000/pending"
            },
            "auto_return": "approved"
        }
        
        # Crear preferencia
        preference_response = sdk.preference().create(preference_data)
        preference = preference_response["response"]
        
        return jsonify({
            'id': preference['id'],
            'init_point': preference['init_point']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/success')
def success():
    return "¡Pago exitoso! Gracias por tu compra."

@app.route('/failure')
def failure():
    return "El pago ha fallado. Intenta nuevamente."

@app.route('/pending')
def pending():
    return "El pago está pendiente de confirmación."

if __name__ == '__main__':
    app.run(debug=True, port=5000)