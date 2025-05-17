import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox)
import mysql.connector

class CategoriasCRUD(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestión de Categorías - Coppel")
        self.setGeometry(100, 100, 600, 400)
        
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
        
        self.lbl_descripcion = QLabel("Descripción:")
        self.txt_descripcion = QLineEdit()
        self.form_layout.addWidget(self.lbl_descripcion)
        self.form_layout.addWidget(self.txt_descripcion)
        
        # Botones
        self.btn_layout = QHBoxLayout()
        self.layout.addLayout(self.btn_layout)
        
        self.btn_crear = QPushButton("Crear")
        self.btn_crear.clicked.connect(self.crear_categoria)
        self.btn_layout.addWidget(self.btn_crear)
        
        self.btn_actualizar = QPushButton("Actualizar")
        self.btn_actualizar.clicked.connect(self.actualizar_categoria)
        self.btn_actualizar.setEnabled(False)
        self.btn_layout.addWidget(self.btn_actualizar)
        
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.clicked.connect(self.eliminar_categoria)
        self.btn_eliminar.setEnabled(False)
        self.btn_layout.addWidget(self.btn_eliminar)
        
        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)
        self.btn_layout.addWidget(self.btn_limpiar)
        
        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(3)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Descripción"])
        self.tabla.cellClicked.connect(self.cargar_datos_formulario)
        self.layout.addWidget(self.tabla)
        
        # Cargar datos iniciales
        self.cargar_categorias()
    
    def cargar_categorias(self):
        try:
            self.cursor.execute("SELECT id_categoria, nombre, descripcion FROM categorias")
            categorias = self.cursor.fetchall()
            
            self.tabla.setRowCount(0)
            for categoria in categorias:
                row = self.tabla.rowCount()
                self.tabla.insertRow(row)
                self.tabla.setItem(row, 0, QTableWidgetItem(str(categoria['id_categoria'])))
                self.tabla.setItem(row, 1, QTableWidgetItem(categoria['nombre']))
                self.tabla.setItem(row, 2, QTableWidgetItem(categoria['descripcion'] if categoria['descripcion'] else ""))
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Error al cargar categorías: {err}")
    
    def crear_categoria(self):
        nombre = self.txt_nombre.text().strip()
        descripcion = self.txt_descripcion.text().strip() or None
        
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
        
        try:
            query = "INSERT INTO categorias (nombre, descripcion) VALUES (%s, %s)"
            valores = (nombre, descripcion)
            self.cursor.execute(query, valores)
            self.conexion.commit()
            
            self.cargar_categorias()
            self.limpiar_formulario()
            QMessageBox.information(self, "Éxito", "Categoría creada correctamente")
        except mysql.connector.Error as err:
            self.conexion.rollback()
            QMessageBox.critical(self, "Error", f"Error al crear categoría: {err}")
    
    def actualizar_categoria(self):
        categoria_id = self.txt_id.text()
        if not categoria_id:
            return
            
        nombre = self.txt_nombre.text().strip()
        descripcion = self.txt_descripcion.text().strip() or None
        
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
            
        try:
            query = "UPDATE categorias SET nombre = %s, descripcion = %s WHERE id_categoria = %s"
            valores = (nombre, descripcion, categoria_id)
            self.cursor.execute(query, valores)
            self.conexion.commit()
            
            self.cargar_categorias()
            QMessageBox.information(self, "Éxito", "Categoría actualizada correctamente")
        except mysql.connector.Error as err:
            self.conexion.rollback()
            QMessageBox.critical(self, "Error", f"Error al actualizar categoría: {err}")
    
    def eliminar_categoria(self):
        categoria_id = self.txt_id.text()
        if not categoria_id:
            return
            
        reply = QMessageBox.question(
            self, "Confirmar", 
            "¿Está seguro de eliminar esta categoría?", 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Verificar si la categoría tiene artículos asociados
                self.cursor.execute("SELECT COUNT(*) FROM articulos WHERE id_categoria = %s", (categoria_id,))
                if self.cursor.fetchone()['COUNT(*)'] > 0:
                    QMessageBox.warning(self, "Error", "No se puede eliminar la categoría porque tiene artículos asociados")
                    return
                
                query = "DELETE FROM categorias WHERE id_categoria = %s"
                valores = (categoria_id,)
                self.cursor.execute(query, valores)
                self.conexion.commit()
                
                self.cargar_categorias()
                self.limpiar_formulario()
                QMessageBox.information(self, "Éxito", "Categoría eliminada correctamente")
            except mysql.connector.Error as err:
                self.conexion.rollback()
                QMessageBox.critical(self, "Error", f"Error al eliminar categoría: {err}")
    
    def cargar_datos_formulario(self, row, column):
        self.txt_id.setText(self.tabla.item(row, 0).text())
        self.txt_nombre.setText(self.tabla.item(row, 1).text())
        self.txt_descripcion.setText(self.tabla.item(row, 2).text())
        
        # Habilitar botones de actualizar y eliminar
        self.btn_actualizar.setEnabled(True)
        self.btn_eliminar.setEnabled(True)
        self.btn_crear.setEnabled(False)
    
    def limpiar_formulario(self):
        self.txt_id.clear()
        self.txt_nombre.clear()
        self.txt_descripcion.clear()
        
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
    window = CategoriasCRUD()
    window.show()
    sys.exit(app.exec())