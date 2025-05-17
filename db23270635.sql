-- Creación de la base de datos 
CREATE DATABASE IF NOT EXISTS coppel_db;
USE coppel_db;

-- Tabla de Clientes
CREATE TABLE clientes (
    id_cliente INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE,
    telefono VARCHAR(15) UNIQUE,
    direccion TEXT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cliente_correo (correo),
    INDEX idx_cliente_telefono (telefono)
);

-- Tabla de Proveedores
CREATE TABLE proveedores (
    id_proveedor INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    contacto VARCHAR(100),
    telefono VARCHAR(15) UNIQUE,
    correo VARCHAR(100) UNIQUE,
    direccion TEXT,
    INDEX idx_proveedor_nombre (nombre)
);

-- Tabla de Categorías
CREATE TABLE categorias (
    id_categoria INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion TEXT
);

-- Tabla de Artículos
CREATE TABLE articulos (
    id_articulo VARCHAR(13) PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10,2) NOT NULL CHECK (precio >= 0),
    stock INT UNSIGNED NOT NULL DEFAULT 0 CHECK (stock >= 0),
    id_categoria INT UNSIGNED,
    id_proveedor INT UNSIGNED,
    marca VARCHAR(50) DEFAULT 'Coppel',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_articulo_categoria FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT fk_articulo_proveedor FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor) ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_articulo_nombre (nombre)
);

-- Tabla de Ventas (reemplazando Pedidos)
CREATE TABLE ventas (
    id_venta INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT UNSIGNED,
    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total DECIMAL(10,2) NOT NULL CHECK (total >= 0),
    estado ENUM('Pendiente', 'Pagado', 'Enviado', 'Entregado', 'Cancelado') DEFAULT 'Pendiente',
    CONSTRAINT fk_venta_cliente FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla de Detalles de Ventas (reemplazando Detalles de Pedido)
CREATE TABLE detalles_venta (
    id_detalle INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_venta INT UNSIGNED,
    id_articulo VARCHAR(13),
    cantidad INT UNSIGNED NOT NULL CHECK (cantidad > 0),
    precio_unitario DECIMAL(10,2) NOT NULL CHECK (precio_unitario >= 0),
    subtotal DECIMAL(10,2) GENERATED ALWAYS AS (cantidad * precio_unitario) STORED,
    CONSTRAINT fk_detalle_venta FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_detalle_articulo FOREIGN KEY (id_articulo) REFERENCES articulos(id_articulo) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Tabla de Métodos de Pago
CREATE TABLE metodos_pago (
    id_metodo INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    metodo VARCHAR(50) NOT NULL UNIQUE
);

-- Insertar métodos de pago por defecto
INSERT INTO metodos_pago (metodo) VALUES ('Efectivo'), ('Tarjeta'), ('Transferencia'), ('PayPal');

-- Tabla de Pagos (actualizada para referenciar ventas)
CREATE TABLE pagos (
    id_pago INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_venta INT UNSIGNED,
    monto DECIMAL(10,2) NOT NULL CHECK (monto >= 0),
    id_metodo INT UNSIGNED NOT NULL,
    fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_pago_venta FOREIGN KEY (id_venta) REFERENCES ventas(id_venta) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_pago_metodo FOREIGN KEY (id_metodo) REFERENCES metodos_pago(id_metodo)
);

-- Trigger para actualizar el stock después de una venta
DELIMITER $$
CREATE TRIGGER actualizar_stock AFTER INSERT ON detalles_venta
FOR EACH ROW
BEGIN
    UPDATE articulos SET stock = stock - NEW.cantidad WHERE id_articulo = NEW.id_articulo;
END $$
DELIMITER ;