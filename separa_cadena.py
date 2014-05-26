# -*- coding: utf-8 -*-
import sys
import datetime
import MySQLdb

linea = '='*40
cadena_original = sys.argv[1]
lista_correcta = []
lista_cambio = []
lista_ingreso = []


   #### Conexión Base de Datos
DB_HOST = 'localhost' 
DB_USER = 'root' 
DB_PASS = '' 
DB_NAME = 'Proyecto' 

def obtener_error(id_error):
    query = "SELECT Descripcion FROM Tabla_Errores WHERE Id = " + id_error
    result = run_query(query)
    return formato_result(result)

def calc_id_venta():
    id_venta = ""
    try:
        query = "SELECT MAX(Id_venta) FROM Tabla_Ventas"
        try: 
                    result = run_query(query)
                    id_venta = formato_result(result)[:-1]
        except MySQLdb.Error, e:
            try:
                print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
            except IndexError:
                print "MySQL Error: %s" % str(e)
                sys.exit(0)
    except:
        print "No se Puede Ejecutar la Consulta"
    return id_venta


def formato_result(result):
    result = str(result[0])
    return  result[1:-2]


def run_query(query=''): 
    datos = [DB_HOST, DB_USER, DB_PASS, DB_NAME] 
 
    conn = MySQLdb.connect(*datos) # Conectar a la base de datos 
    cursor = conn.cursor()         # Crear un cursor 
    cursor.execute(query)          # Ejecutar una consulta 
 
    if query.upper().startswith('SELECT'): 
        data = cursor.fetchall()   # Traer los resultados de un select 
    else: 
        conn.commit()              # Hacer efectiva la escritura de datos 
        data = None 
 
        cursor.close()                 # Cerrar el cursor 
        conn.close()                   # Cerrar la conexión 
 
        return data

def separar_dinero(cantidad,id_venta,tabla):
    cambio_correcto = [] 
    cantidad = cantidad.split(';')
    for elementos in cantidad:
            elementos = elementos.split(',')
            cambio_correcto = []
            for i in elementos:
                cambio_correcto.append(i)
                query ="INSERT INTO " + tabla + " VALUES(NULL, '" \
                            + id_venta + "', '"\
                            + cambio_correcto[0] + "' , '"\
                            + cambio_correcto[1] + "' , '"\
                            + cambio_correcto[2] + "');" 
                try:
                   run_query(query)
        
                except MySQLdb.Error, e:
                    try:
                        print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
                    except IndexError:
                            print "MySQL Error: %s" % str(e)
                            sys.exit(0)

    return


#cadena_original = '\x02AC10TX1241213172|1|2014-02-03|18:02:00|299|0|3.00|1|3.00|10.00|M,10.00,1|M,2.0,1;M,5.0,1|1554\x03'
#  Buscar el Incio y fin de la cadena

inicio_cadena = cadena_original.find('\x02')
fin_cadena = cadena_original.find('\x03')
if inicio_cadena != 0:
    print obtener_error('1')
elif fin_cadena == -1:
    print obtener_error('2')
else:
    cadena = cadena_original[1:-1]
    fin = len(cadena)-3

    # Optiene el check sum de la cadena
    check_sum_cadena = cadena_original[fin:-1]
    cadena = cadena[:-4]
    check_sum_calculado =0
    
    # Calcula el check sum
    for letra in cadena:
            check_sum_calculado += ord(letra)
        
    # Convierte el check sum de la cadena a decimal
    check_sum_cadena = int(check_sum_cadena.lower(),16 )
    if check_sum_calculado != check_sum_cadena:
        print obtener_error('19')
    else:
        cadena = cadena[:-1]
        lista = cadena.split('|')
                                # // Revisar que se salga del programa cuando la cadena esta incompleta 
        # Comprobación de la cantidad de datos 
        if len(lista) < 11:
            print obtener_error('3')
        elif len(lista) > 12:
            print obtener_error('4')
        else:
                # /// Numero de serie ///
            if len(lista[0]) < 3 or len(lista[0]) > 16:
                print "Error número de serie incorrecto"
                sys.exit(0)  
            else: 
                lista_correcta.append(lista[0])

                # /// Número de turno ///                
            try:
                numero_turno = int(lista[1])
            except ValueError:
                print "Tipo de dato invalido en turno"
                sys.exit(0)

            if numero_turno <= 0 or numero_turno > 999999:
                print "Error en el número de turno fuera de rango"
                sys.exit(0)
            else:
                lista_correcta.append(int(lista[1]))
            
                # /// Fecha ///
            try:
                fecha = lista[2]  
                fecha = datetime.datetime.strptime(fecha, '%Y-%m-%d').date()
                lista_correcta.append(fecha)
            except:        
                print "Tipo de dato invalido en fecha"
                sys.exit(0)
            
                # /// Hora ///
            try:    
                hora = lista[3]
                hora = datetime.datetime.strptime(hora, '%H:%M:%S').time()
                lista_correcta.append(hora)
            except:
                print "Error dato invalido en la hora"
                sys.exit(0)

                # /// Número de ticket ///
            try:
                lista_correcta.append(long(lista[4]))
            except:
                print "Error en el tipo de dato del Ticket"    
                sys.exit(0)
                
                # /// Detalle de la venta ///
            try:
                detalle_venta = int(lista[5])
                if detalle_venta == 0:
                    lista_correcta.append(detalle_venta)
                else:
                    print "No se puede dar más detalles de la venta"
                     #sys.exit(0)

            except:
                print "Erro en el tipo de dato de detalle"
                sys.exit(0)
            
                # /// Tarifa ///
            try:
                lista_correcta.append(float(lista[6]))
            except:
                print "Error en el tipo de dato de la tarifa"
                sys.exit(0)
            
                # /// Multiplicador //
            try:
                multiplicador = int(lista[7])
                if multiplicador <= 0 or multiplicador > 40:
                    print multiplicador
                    print "Error el multiplicador no es correcto"    
                    sys.exit(0)

                else:
                    lista_correcta.append(multiplicador)
            except:
                print "Error en el tipo de dato del multiplicador"
                sys.exit(0)

                # /// Total ///
            try:
                total = float(lista[8])
                if total != (lista_correcta[6] * multiplicador):
                    print "Error el total no es correcto"
                else:
                    lista_correcta.append(total)
            except:
                print "Error en el tipo de dato de total"
                sys.exit(0)

                # /// Deposito ///
            try:
                deposito = float(lista[9])
                if deposito < 0:
                    print "Error el deposito no puede ser un número negativo"
                    sys.exit(0)
                else:
                    lista_correcta.append(deposito)
            except:
                print "Error en el tipo de dato de deposito"
                sys.exit(0)
                # /// Ingreso ///

            if lista[10].lower() == 't' and deposito == 0:
                    lista_correcta.append('T')


            else:
                query = "INSERT INTO Tabla_Ventas(No_serie,Turno,Fecha,Hora,Ticket,No_detalle,Tarifa,Multiplicador,Total,Deposito) VALUES('"\
                                                        + str(lista_correcta[0]) + "' ,' "\
                                                        + str(lista_correcta[1]) + "' , '" \
                                                        + str(lista_correcta[2]) + "' , '"\
                                                        + str(lista_correcta[3]) + "',' "\
                                                        + str(lista_correcta[4]) + "' ,' "\
                                                        + str(lista_correcta[5]) + "' ,' "\
                                                        + str(lista_correcta[6]) + "' ,' "\
                                                        + str(lista_correcta[7]) + "' , ' "\
                                                        + str(lista_correcta[8]) + "' ,' "\
                                                        + str(lista_correcta[9]) + "');"
                try:
                                    run_query(query)
                
                except MySQLdb.Error, e:                                                    #
                        try:                                                                #
                            print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])           #
                        except IndexError:                                                  #    obtiene los errores de MySql
                            print "MySQL Error: %s" % str(e)                                #
                        sys.exit(0)                                                         #
                try:                           
                    ingreso = lista[10]    
                    separar_dinero(ingreso,calc_id_venta(),'Ingreso_Venta')
                except:                                    
                    print "Error en el formato del Ingreso"
                    print ingreso        
                    sys.exit(0)
                    
                    # /// Cambio ///
                try:
                    cambio = lista[11]
                    separar_dinero(cambio,calc_id_venta(),'Cambio_Venta')
                except:
                    print "Error en formato del cambio"
                    sys.exit(0)
                        