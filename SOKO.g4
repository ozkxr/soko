grammar SOKO;

program
    : statement* EOF
    ;

statement
    : configPin
    | setPin
    | bucleWhile
    | bucleRepeat
    | condicionalIf
    | sleepCmd
    | comentario
    ;

configPin
    : CONFIG PIN INT pinMode
    ;
    
pinMode
    : (OUT | IN | ANALOG_IN | ANALOG_OUT)
    ;

setPin
    : SET PIN INT '=' value
    ;

value
    : ON
    | OFF
    | numero
    ;

numero
    : FLOAT
    | INT
    ;

bucleWhile
    : WHILE '(' condition ')' DO statement* ENDWHILE
    ;

bucleRepeat
    : REPEAT INT DO statement* ENDREPEAT
    ;

condicionalIf
    : IF '(' condition ')' THEN statement* (ELSE statement*)? ENDIF
    ;

condition
    : '!'? PIN INT (comparador value)?
    ;

comparador
    : '=='
    | '!='
    | '>='
    | '<='
    | '>'
    | '<'
    ;

sleepCmd
    : SLEEP INT
    ;

comentario
    : COMENTARIO
    ;

// PALABRAS CLAVE

CONFIG    : 'CONFIG' ;
OUT       : 'OUT' ;
IN        : 'IN' ;
ANALOG_IN : 'ANALOG_IN' ;
ANALOG_OUT: 'ANALOG_OUT' ;
SET       : 'SET' ;
WHILE     : 'WHILE' ;
DO        : 'DO' ;
ENDWHILE  : 'ENDWHILE' ;
REPEAT    : 'REPEAT' ;
ENDREPEAT : 'ENDREPEAT' ;
IF        : 'IF' ;
THEN      : 'THEN' ;
ENDIF     : 'ENDIF' ;
ELSE      : 'ELSE' ;
SLEEP     : 'SLEEP' ;
PIN       : 'PIN' ;
ON        : 'ON' ;
OFF       : 'OFF' ;

FLOAT     : [0-9]+ '.' [0-9]+ ;
INT       : [0-9]+ ;
COMENTARIO: '#' ~[\r\n]* -> skip ;
WS        : [ \t\r\n]+ -> skip ;
