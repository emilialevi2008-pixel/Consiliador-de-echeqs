# Conciliador de cheques

Autora: Emilia Agustina Levi.
Trabajo Práctico 2 — Programación Orientada a Datos.

## Problema

Comparar manualmente los cheques de un banco con los registrados
en un sistema de gestión lleva tiempo y puede producir errores.

## Objetivo

Crear un programa en Python que compare ambos archivos e identifique
los cheques conciliados, los que tienen diferencias y los que aparecen
únicamente en uno de los archivos.

## Usuarios

Personal administrativo y contable que necesite revisar cheques.

## Funcionalidades previstas

- Leer archivos CSV y JSON.
- Incorporar lectura de Excel como función adicional.
- Comparar identificadores completos y abreviados sin ambigüedad.
- Comparar importes y fechas de cobro o pago.
- Mostrar las fechas en formato DD/MM/AAAA.
- Comparar todos los registros o un período elegido por el usuario.
- Detectar duplicados y datos inválidos.
- Calcular totales y generar reportes detallados.

## Alcance

El programa funcionará desde la consola y utilizará datos ficticios
para las pruebas. No se conectará con bancos reales ni realizará
operaciones financieras.
