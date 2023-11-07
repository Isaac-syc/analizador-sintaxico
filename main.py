import re
import ast
import sys
from PyQt5 import QtWidgets, uic


exp = {
    "Nombres": r"[a-z][a-z0-9]*",
    "Letras": r"[a-z]+",
    "Asignacion": r"=",
    "Operadores": r"(==|!=|>|<|>=|<=)",
    "ValorDigitos": r"\d+",
    "ValorTextos": r"\"[^\"]*\"",
    "PalabraResFor": r"for",
    "PalabraResIf": r"if",
    "PalabraResMain": r"main",
    "PalabraResFn": r"fn",
    "ParentesisApertura": r"\(",
    "ParentesisCierre": r"\)",
    "LlavesContenido": r"\{(.*?)\}",
    "Coma": r",",
}


exp["LlamadaFuncion"] = fr"{exp['Nombres']}\s*{exp['ParentesisApertura']}.*?{exp['ParentesisCierre']}"


def construir_regla(*args):
    return r"^\s*" + r"\s*".join(args) + r"\s*$"


def validar_variable(cadena):
    regla = construir_regla(exp['Nombres'], exp['Asignacion'], f"({exp['ValorDigitos']}|{exp['ValorTextos']})")
    return re.fullmatch(regla, cadena) is not None

def validar_llamada_funcion(cadena):
    regla = construir_regla(exp['Nombres'], exp['ParentesisApertura'] + r".*?" + exp['ParentesisCierre'])
    return re.fullmatch(regla, cadena) is not None

def validar_if(cadena):
    regla = construir_regla(exp['PalabraResIf'], exp['ParentesisApertura'], exp['Nombres'], exp['Operadores'], 
                            f"({exp['ValorDigitos']}|{exp['ValorTextos']}|{exp['Nombres']})", exp['ParentesisCierre'], r"\{.*?\}")
    return re.fullmatch(regla, cadena, re.DOTALL) is not None

def validar_for(cadena):
    regla = construir_regla(exp['PalabraResFor'], exp['ParentesisApertura'], exp['Nombres'], exp['Coma'], 
                            exp['ValorDigitos'], exp['Coma'], exp['ValorDigitos'], exp['ParentesisCierre'], r"\{.*?\}")
    return re.fullmatch(regla, cadena, re.DOTALL) is not None

def validar_funcion(cadena):
    parametros = f"({exp['Nombres']}(?:\s*{exp['Coma']}\s*{exp['Nombres']})*)?"
    regla = construir_regla(exp['PalabraResFn'], exp['Nombres'], exp['ParentesisApertura'], parametros, 
                            exp['ParentesisCierre'], r"\{.*?\}")
    return re.fullmatch(regla, cadena, re.DOTALL) is not None

def validar_main(cadena):
    regla = construir_regla(exp['PalabraResMain'], exp['ParentesisApertura'], exp['ParentesisCierre'], r"\{.*?\}")
    return re.fullmatch(regla, cadena, re.DOTALL) is not None

def validar_bloque(bloque, GUI):
    lineas = bloque.split('\n')
    profundidad_llaves = 0 
    for i, linea in enumerate(lineas):
        linea = linea.strip()
        profundidad_llaves += linea.count('{')
        profundidad_llaves -= linea.count('}')
        if not linea or linea == '{' or linea == '}':
            continue
 
        if any(linea.startswith(kw) and linea.endswith('{') for kw in ['if ', 'for ', 'fn ', 'main']):
  
            
            
            
            llaves_abiertas = 1
            inicio_bloque = i
            while i < len(lineas) and llaves_abiertas > 0:
                llaves_abiertas += lineas[i].count('{')
                llaves_abiertas -= lineas[i].count('}')
                i += 1
           
            bloque_completo = '\n'.join(lineas[inicio_bloque:i])
            if linea.startswith('if ') and not validar_if(bloque_completo):
                GUI.transitionsBrowser.setPlainText("error de sintaxis en: " + linea)
                print("error de sintaxis en: " + linea)
                return False
            elif linea.startswith('for ') and not validar_for(bloque_completo):
                GUI.transitionsBrowser.setPlainText("error de sintaxis en: " + linea)
                print("error de sintaxis en: " + linea)
                return False
            elif linea.startswith('fn ') and not validar_funcion(bloque_completo):
                GUI.transitionsBrowser.setPlainText("error de sintaxis en: " + linea)
                print("error de sintaxis en: " + linea)
                return False
            elif linea.startswith('main') and not validar_main(bloque_completo):
                GUI.transitionsBrowser.setPlainText("error de sintaxis en: " + linea)
                print("error de sintaxis en: " + linea)
                return False
            
        else:
           
            if not (validar_variable(linea) or validar_llamada_funcion(linea)):
                GUI.transitionsBrowser.setPlainText("error de declaracion en: " + linea)
                print("error de declaracion en: " + linea)
                return False
            
       
    if profundidad_llaves != 0:
        GUI.transitionsBrowser.setPlainText("Error de sintaxis: llave no esperada: " + linea)
        print("Error de sintaxis: llave no esperada: " + lineas[0])
        return False   
    return True


def analizar_bloques(codigo, GUI):
    GUI.transitionsBrowser.clear()
    
    declaraciones = codigo.strip().split('\n')
    
    bloque_valido = validar_bloque('\n'.join(declaraciones), GUI)
    if bloque_valido:
        print("Todo el código es válido.")
        GUI.transitionsBrowser.setPlainText('Todo el código es válido')
    else:
        print("Bloque inválido. Hay un error en el código.")

def getData(GUI):
    
    code_editor = GUI.findChild(QtWidgets.QPlainTextEdit, 'codeEditor')

  
    code = code_editor.toPlainText()
    analizar_bloques(code, GUI)
    
    


if __name__ == "__main__":   
   app = QtWidgets.QApplication(sys.argv)
   GUI = uic.loadUi("interfaz.ui")
   GUI.show()

   
   GUI.evaluate_test.clicked.connect(lambda: getData(GUI))

   sys.exit(app.exec_())