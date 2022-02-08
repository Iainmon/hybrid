grammar HybLang;



IDENTIFIER  :   [a-zA-Z]+ ;      // match identifiers <label id="code.tour.expr.3"/>
NUMBER :   [0-9]+ ;         // match integers
NEWLINE:'\r'? '\n' -> skip;     // return newlines to parser (is end-statement signal)
WS  :   [ \t]+ -> skip ; // toss out whitespace
SET_LIT : [0-9a-zA-Z];


LPAREN : '(';
RPAREN : ')';
LBRACK : '{';
RBRACK : '}';
ASSIGN: ':=';
SAMPLE: '<-';
SEPARATOR : ';';
SEQSEP : ',';
BLOCKSTART : ':';
LSQBRACK : '[';
RSQBRACK : ']';
BIN_OP : '+' | '-' | '*' | '/' | 'xor' | '&' | '||' | '^' | 'is';

// program: statement (NEWLINE+ statement)* NEWLINE*;
program: procedure;

bin_op: '+' | '-' | '*' | '/' | 'xor' | '&' | '||' | '^' | 'is';

identifier : IDENTIFIER;

function_call: IDENTIFIER LPAREN (expression (',' expression)*)? RPAREN;

expression : LPAREN expression RPAREN
           | expression bin_op expression
           | NUMBER
           | IDENTIFIER
           | function_call
           ;
assignment : IDENTIFIER ':=' expression;
sample : IDENTIFIER '<-' (set_type|expression);

return_stmt: 'return' expression;

statement : assignment
          | sample 
          | return_stmt
          | expression 
          ;

// procedure : statement (NEWLINE+ statement)* NEWLINE*;
procedure : (non_statement | query_statement | statement ';'+)* ;
non_statement : function_def | if_stmt | call_prog_def | library_def;
// procedure : statement NEWLINE? | procedureRec;
// procedureRec : statement NEWLINE procedure NEWLINE*;

set_lit : '\'' IDENTIFIER '\'' | NUMBER;
set_type : '{' set_lit (',' set_lit)* '}' | 'bin' '(' NUMBER ')';

function_argument : IDENTIFIER (':' set_type)? ;
// | identifier ':' set_type ;
function_arguments : function_argument (',' function_argument)*;
function_def : ('rout'|'def'|'func') IDENTIFIER '(' function_arguments? ')' block;

block : ':' '{' procedure '}';

if_stmt : 'if' expression 'then'  block ('else' block)?;

call_prog_def : ('pro'|'program') '[' IDENTIFIER ']' block ;
exposing_sequence : ('rout'|'func'|'var') IDENTIFIER (','('func'|'var') IDENTIFIER)*;
library_def : ('lib' | 'library') '[' IDENTIFIER ']' ('exposing' '(' exposing_sequence? ')')? block;


query_statement : show_query_statement ;
show_query_statement : 'show' query_expression '.';
query_relation : '<>' | '==' | '~=' | '=>' ;
query_expression : LPAREN query_expression RPAREN 
                 | query_expression query_relation query_expression 
                 | ('pro' | 'program' | 'lib' | 'library') '[' IDENTIFIER ']'
                 | IDENTIFIER 
                 ;
