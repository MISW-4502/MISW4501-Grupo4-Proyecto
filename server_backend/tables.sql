
CREATE TABLE camion (
	camion_id SERIAL NOT NULL, 
	placa VARCHAR(50) NOT NULL, 
	capacidad NUMERIC(12, 2) NOT NULL, 
	tipo VARCHAR(50), 
	fecha_registro TIMESTAMP WITHOUT TIME ZONE, 
	rutas TEXT, 
	PRIMARY KEY (camion_id), 
	UNIQUE (placa)
)




CREATE TABLE fabricante (
	fabricante_id SERIAL NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	pais_origen VARCHAR(100), 
	creado_en TIMESTAMP WITHOUT TIME ZONE, 
	categoria VARCHAR(100), 
	PRIMARY KEY (fabricante_id)
)




CREATE TABLE pedido (
	pedido_id SERIAL NOT NULL, 
	id_cliente INTEGER NOT NULL, 
	id_vendedor INTEGER, 
	fecha_creacion TIMESTAMP WITHOUT TIME ZONE, 
	estado VARCHAR(50), 
	total NUMERIC(14, 2), 
	PRIMARY KEY (pedido_id)
)




CREATE TABLE producto (
	producto_id SERIAL NOT NULL, 
	nombre VARCHAR(150) NOT NULL, 
	descripcion TEXT, 
	precio_unitario NUMERIC(12, 2), 
	creado_en TIMESTAMP WITHOUT TIME ZONE, 
	tipo TEXT, 
	cantidad INTEGER, 
	ubicacion TEXT, 
	PRIMARY KEY (producto_id)
)




CREATE TABLE restablecimieno_password (
	id SERIAL NOT NULL, 
	email VARCHAR NOT NULL, 
	token VARCHAR NOT NULL, 
	expires_at TIMESTAMP WITHOUT TIME ZONE, 
	PRIMARY KEY (id), 
	UNIQUE (token)
)




CREATE TABLE usuario (
	usuario_id SERIAL NOT NULL, 
	rol NOT NULL, 
	nombre VARCHAR(100) NOT NULL, 
	email VARCHAR(150) NOT NULL, 
	password VARCHAR(255) NOT NULL, 
	PRIMARY KEY (usuario_id), 
	UNIQUE (email)
)




CREATE TABLE visita (
	visita_id SERIAL NOT NULL, 
	id_vendedor INTEGER NOT NULL, 
	id_cliente INTEGER NOT NULL, 
	fecha_visita TIMESTAMP WITHOUT TIME ZONE NOT NULL, 
	estado VARCHAR(50), 
	descripcion TEXT, 
	direccion TEXT, 
	PRIMARY KEY (visita_id)
)




CREATE TABLE detalle_pedido (
	detalle_id SERIAL NOT NULL, 
	id_pedido INTEGER, 
	id_producto INTEGER NOT NULL, 
	cantidad INTEGER NOT NULL, 
	precio_unitario NUMERIC(12, 2) NOT NULL, 
	subtotal NUMERIC(14, 2) NOT NULL, 
	PRIMARY KEY (detalle_id), 
	FOREIGN KEY(id_pedido) REFERENCES pedido (pedido_id) ON DELETE CASCADE
)

