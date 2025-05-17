import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox)
import mysql.connector

class ProveedoresCRUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Proveedores - Coppel")
        self.setGeometry(100, 100, 900, 600)
        
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
        self.form_layout = QVBoxLayout()
        self.layout.addLayout(self.form_layout)
        
        # Campos del formulario - Fila 1
        self.row1_layout = QHBoxLayout()
        self.form_layout.addLayout(self.row1_layout)
        
        self.lbl_id = QLabel("ID:")
        self.txt_id = QLineEdit()
        self.txt_id.setReadOnly(True)
        self.row1_layout.addWidget(self.lbl_id)
        self.row1_layout.addWidget(self.txt_id)
        
        self.lbl_nombre = QLabel("Nombre:")
        self.txt_nombre = QLineEdit()
        self.row1_layout.addWidget(self.lbl_nombre)
        self.row1_layout.addWidget(self.txt_nombre)
        
        # Campos del formulario - Fila 2
        self.row2_layout = QHBoxLayout()
        self.form_layout.addLayout(self.row2_layout)
        
        self.lbl_contacto = QLabel("Contacto:")
        self.txt_contacto = QLineEdit()
        self.row2_layout.addWidget(self.lbl_contacto)
        self.row2_layout.addWidget(self.txt_contacto)
        
        self.lbl_telefono = QLabel("Teléfono:")
        self.txt_telefono = QLineEdit()
        self.row2_layout.addWidget(self.lbl_telefono)
        self.row2_layout.addWidget(self.txt_telefono)
        
        # Campos del formulario - Fila 3
        self.row3_layout = QHBoxLayout()
        self.form_layout.addLayout(self.row3_layout)
        
        self.lbl_correo = QLabel("Correo:")
        self.txt_correo = QLineEdit()
        self.row3_layout.addWidget(self.lbl_correo)
        self.row3_layout.addWidget(self.txt_correo)
        
        self.lbl_direccion = QLabel("Dirección:")
        self.txt_direccion = QLineEdit()
        self.row3_layout.addWidget(self.lbl_direccion)
        self.row3_layout.addWidget(self.txt_direccion)
        
        # Botones
        self.btn_layout = QHBoxLayout()
        self.layout.addLayout(self.btn_layout)
        
        self.btn_crear = QPushButton("Crear")
        self.btn_crear.clicked.connect(self.crear_proveedor)
        self.btn_layout.addWidget(self.btn_crear)
        
        self.btn_actualizar = QPushButton("Actualizar")
        self.btn_actualizar.clicked.connect(self.actualizar_proveedor)
        self.btn_actualizar.setEnabled(False)
        self.btn_layout.addWidget(self.btn_actualizar)
        
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.clicked.connect(self.eliminar_proveedor)
        self.btn_eliminar.setEnabled(False)
        self.btn_layout.addWidget(self.btn_eliminar)
        
        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)
        self.btn_layout.addWidget(self.btn_limpiar)
        
        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Contacto", "Teléfono", "Correo", "Dirección"])
        self.tabla.cellClicked.connect(self.cargar_datos_formulario)
        self.layout.addWidget(self.tabla)
        
        # Cargar datos iniciales
        self.cargar_proveedores()
    
    def cargar_proveedores(self):
        try:
            self.cursor.execute("SELECT id_proveedor, nombre, contacto, telefono, correo, direccion FROM proveedores")
            proveedores = self.cursor.fetchall()
            
            self.tabla.setRowCount(0)
            for proveedor in proveedores:
                row = self.tabla.rowCount()
                self.tabla.insertRow(row)
                self.tabla.setItem(row, 0, QTableWidgetItem(str(proveedor['id_proveedor'])))
                self.tabla.setItem(row, 1, QTableWidgetItem(proveedor['nombre']))
                self.tabla.setItem(row, 2, QTableWidgetItem(proveedor['contacto'] if proveedor['contacto'] else ""))
                self.tabla.setItem(row, 3, QTableWidgetItem(proveedor['telefono'] if proveedor['telefono'] else ""))
                self.tabla.setItem(row, 4, QTableWidgetItem(proveedor['correo'] if proveedor['correo'] else ""))
                self.tabla.setItem(row, 5, QTableWidgetItem(proveedor['direccion'] if proveedor['direccion'] else ""))
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Error al cargar proveedores: {err}")
    
    def crear_proveedor(self):
        nombre = self.txt_nombre.text().strip()
        contacto = self.txt_contacto.text().strip() or None
        telefono = self.txt_telefono.text().strip() or None
        correo = self.txt_correo.text().strip() or None
        direccion = self.txt_direccion.text().strip() or None
        
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
        
        try:
            query = """INSERT INTO proveedores 
                       (nombre, contacto, telefono, correo, direccion) 
                       VALUES (%s, %s, %s, %s, %s)"""
            valores = (nombre, contacto, telefono, correo, direccion)
            self.cursor.execute(query, valores)
            self.conexion.commit()
            
            self.cargar_proveedores()
            self.limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Proveedor creado correctamente")
        except mysql.connector.Error as err:
            self.conexion.rollback()
            QMessageBox.critical(self, "Error", f"Error al crear proveedor: {err}")
    
    def actualizar_proveedor(self):
        proveedor_id = self.txt_id.text()
        if not proveedor_id:
            return
            
        nombre = self.txt_nombre.text().strip()
        contacto = self.txt_contacto.text().strip() or None
        telefono = self.txt_telefono.text().strip() or None
        correo = self.txt_correo.text().strip() or None
        direccion = self.txt_direccion.text().strip() or None
        
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
            
        try:
            query = """UPDATE proveedores SET 
                       nombre = %s, contacto = %s, telefono = %s, 
                       correo = %s, direccion = %s 
                       WHERE id_proveedor = %s"""
            valores = (nombre, contacto, telefono, correo, direccion, proveedor_id)
            self.cursor.execute(query, valores)
            self.conexion.commit()
            
            self.cargar_proveedores()
            QMessageBox.information(self, "Éxito", "Proveedor actualizado correctamente")
        except mysql.connector.Error as err:
            self.conexion.rollback()
            QMessageBox.critical(self, "Error", f"Error al actualizar proveedor: {err}")
    
    def eliminar_proveedor(self):
        proveedor_id = self.txt_id.text()
        if not proveedor_id:
            return
            
        reply = QMessageBox.question(
            self, "Confirmar", 
            "¿Está seguro de eliminar este proveedor?", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Verificar si el proveedor tiene artículos asociados
                self.cursor.execute("SELECT COUNT(*) FROM articulos WHERE id_proveedor = %s", (proveedor_id,))
                if self.cursor.fetchone()['COUNT(*)'] > 0:
                    QMessageBox.warning(self, "Error", "No se puede eliminar el proveedor porque tiene artículos asociados")
                    return
                
                query = "DELETE FROM proveedores WHERE id_proveedor = %s"
                valores = (proveedor_id,)
                self.cursor.execute(query, valores)
                self.conexion.commit()
                
                self.cargar_proveedores()
                self.limpiar_formulario()
                QMessageBox.information(self, "Éxito", "Proveedor eliminado correctamente")
            except mysql.connector.Error as err:
                self.conexion.rollback()
                QMessageBox.critical(self, "Error", f"Error al eliminar proveedor: {err}")
    
    def cargar_datos_formulario(self, row, column):
        self.txt_id.setText(self.tabla.item(row, 0).text())
        self.txt_nombre.setText(self.tabla.item(row, 1).text())
        self.txt_contacto.setText(self.tabla.item(row, 2).text())
        self.txt_telefono.setText(self.tabla.item(row, 3).text())
        self.txt_correo.setText(self.tabla.item(row, 4).text())
        self.txt_direccion.setText(self.tabla.item(row, 5).text())
        
        # Habilitar botones de actualizar y eliminar
        self.btn_actualizar.setEnabled(True)
        self.btn_eliminar.setEnabled(True)
        self.btn_crear.setEnabled(False)
    
    def limpiar_formulario(self):
        self.txt_id.clear()
        self.txt_nombre.clear()
        self.txt_contacto.clear()
        self.txt_telefono.clear()
        self.txt_correo.clear()
        self.txt_direccion.clear()
        
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
    window = ProveedoresCRUD()
    window.show()
    sys.exit(app.exec())