import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox)
from PyQt6.QtCore import QDateTime
import mysql.connector

class ClientesCRUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Clientes - Coppel")
        self.setGeometry(100, 100, 800, 600)
        
        # Conexión a la base de datos
        self.conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="xx_cross3854_xx",
            database="coppel_db"
        )
        
        if not self.conexion.is_connected():
            QMessageBox.critical(self, "Error", "No se pudo conectar a la base de datos")
            sys.exit(1)
            
        self.cursor = self.conexion.cursor(dictionary=True)
        
        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout principal
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        # Formulario
        self.form_layout = QHBoxLayout()
        self.layout.addLayout(self.form_layout)
        
        # Campos del formulario
        self.lbl_id = QLabel("ID:")
        self.txt_id = QLineEdit()
        self.txt_id.setReadOnly(True)
        self.form_layout.addWidget(self.lbl_id)
        self.form_layout.addWidget(self.txt_id)
        
        self.lbl_nombre = QLabel("Nombre:")
        self.txt_nombre = QLineEdit()
        self.form_layout.addWidget(self.lbl_nombre)
        self.form_layout.addWidget(self.txt_nombre)
        
        self.lbl_correo = QLabel("Correo:")
        self.txt_correo = QLineEdit()
        self.form_layout.addWidget(self.lbl_correo)
        self.form_layout.addWidget(self.txt_correo)
        
        self.lbl_telefono = QLabel("Teléfono:")
        self.txt_telefono = QLineEdit()
        self.form_layout.addWidget(self.lbl_telefono)
        self.form_layout.addWidget(self.txt_telefono)
        
        # Botones
        self.btn_layout = QHBoxLayout()
        self.layout.addLayout(self.btn_layout)
        
        self.btn_crear = QPushButton("Crear")
        self.btn_crear.clicked.connect(self.crear_cliente)
        self.btn_layout.addWidget(self.btn_crear)
        
        self.btn_actualizar = QPushButton("Actualizar")
        self.btn_actualizar.clicked.connect(self.actualizar_cliente)
        self.btn_actualizar.setEnabled(False)
        self.btn_layout.addWidget(self.btn_actualizar)
        
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.clicked.connect(self.eliminar_cliente)
        self.btn_eliminar.setEnabled(False)
        self.btn_layout.addWidget(self.btn_eliminar)
        
        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)
        self.btn_layout.addWidget(self.btn_limpiar)
        
        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Correo", "Teléfono", "Fecha Registro"])
        self.tabla.cellClicked.connect(self.cargar_datos_formulario)
        self.layout.addWidget(self.tabla)
        
        # Cargar datos iniciales
        self.cargar_clientes()
    
    def cargar_clientes(self):
        try:
            self.cursor.execute("SELECT id_cliente, nombre, correo, telefono, fecha_registro FROM clientes")
            clientes = self.cursor.fetchall()
            
            self.tabla.setRowCount(0)
            for cliente in clientes:
                row = self.tabla.rowCount()
                self.tabla.insertRow(row)
                self.tabla.setItem(row, 0, QTableWidgetItem(str(cliente['id_cliente'])))
                self.tabla.setItem(row, 1, QTableWidgetItem(cliente['nombre']))
                self.tabla.setItem(row, 2, QTableWidgetItem(cliente['correo'] if cliente['correo'] else ""))
                self.tabla.setItem(row, 3, QTableWidgetItem(cliente['telefono'] if cliente['telefono'] else ""))
                self.tabla.setItem(row, 4, QTableWidgetItem(str(cliente['fecha_registro'])))
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Error al cargar clientes: {err}")
    
    def crear_cliente(self):
        nombre = self.txt_nombre.text().strip()
        correo = self.txt_correo.text().strip() or None  # Convertir cadena vacía a NULL
        telefono = self.txt_telefono.text().strip() or None
        
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
        
        try:
            query = "INSERT INTO clientes (nombre, correo, telefono) VALUES (%s, %s, %s)"
            valores = (nombre, correo, telefono)
            self.cursor.execute(query, valores)
            self.conexion.commit()
            
            self.cargar_clientes()
            self.limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Cliente creado correctamente")
        except mysql.connector.Error as err:
            self.conexion.rollback()
            QMessageBox.critical(self, "Error", f"Error al crear cliente: {err}")
    
    def actualizar_cliente(self):
        cliente_id = self.txt_id.text()
        if not cliente_id:
            return
            
        nombre = self.txt_nombre.text().strip()
        correo = self.txt_correo.text().strip() or None
        telefono = self.txt_telefono.text().strip() or None
        
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
            
        try:
            query = "UPDATE clientes SET nombre = %s, correo = %s, telefono = %s WHERE id_cliente = %s"
            valores = (nombre, correo, telefono, cliente_id)
            self.cursor.execute(query, valores)
            self.conexion.commit()
            
            self.cargar_clientes()
            QMessageBox.information(self, "Éxito", "Cliente actualizado correctamente")
        except mysql.connector.Error as err:
            self.conexion.rollback()
            QMessageBox.critical(self, "Error", f"Error al actualizar cliente: {err}")
    
    def eliminar_cliente(self):
        cliente_id = self.txt_id.text()
        if not cliente_id:
            return
            
        reply = QMessageBox.question(
            self, "Confirmar", 
            "¿Está seguro de eliminar este cliente?", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Primero verificar si el cliente tiene ventas asociadas
                self.cursor.execute("SELECT COUNT(*) FROM ventas WHERE id_cliente = %s", (cliente_id,))
                if self.cursor.fetchone()['COUNT(*)'] > 0:
                    QMessageBox.warning(self, "Error", "No se puede eliminar el cliente porque tiene ventas asociadas")
                    return
                
                query = "DELETE FROM clientes WHERE id_cliente = %s"
                valores = (cliente_id,)
                self.cursor.execute(query, valores)
                self.conexion.commit()
                
                self.cargar_clientes()
                self.limpiar_formulario()
                QMessageBox.information(self, "Éxito", "Cliente eliminado correctamente")
            except mysql.connector.Error as err:
                self.conexion.rollback()
                QMessageBox.critical(self, "Error", f"Error al eliminar cliente: {err}")
    
    def cargar_datos_formulario(self, row, column):
        self.txt_id.setText(self.tabla.item(row, 0).text())
        self.txt_nombre.setText(self.tabla.item(row, 1).text())
        self.txt_correo.setText(self.tabla.item(row, 2).text())
        self.txt_telefono.setText(self.tabla.item(row, 3).text())
        
        # Habilitar botones de actualizar y eliminar
        self.btn_actualizar.setEnabled(True)
        self.btn_eliminar.setEnabled(True)
        self.btn_crear.setEnabled(False)
    
    def limpiar_formulario(self):
        self.txt_id.clear()
        self.txt_nombre.clear()
        self.txt_correo.clear()
        self.txt_telefono.clear()
        
        # Restablecer botones
        self.btn_crear.setEnabled(True)
        self.btn_actualizar.setEnabled(False)
        self.btn_eliminar.setEnabled(False)
    
    def closeEvent(self, event):
        # Cerrar la conexión a la base de datos al salir
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conexion') and self.conexion.is_connected():
            self.conexion.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ClientesCRUD()
    window.show()
    sys.exit(app.exec())