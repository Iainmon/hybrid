
import Prelude hiding (lookup)
import Control.Monad (join)
import Data.Functor ((<&>))

type Name = String

data Type
  = TLit Name
  | TFun Type Type
  | TPar Name Type Type -- I am assuming you can't look inside proofs
  | TDep Expr
  | TApp Type Type
  | Sort
  deriving Eq
  -- deriving (Show,Eq)
instance Show Type where
  show (TLit n)      = n
  show (TFun t1 t2)  = "(" ++ show t1 ++ " -> " ++ show t2 ++ ")"
  show (TPar n t t') = "Π(" ++ n ++ ":" ++ show t ++ ")"++ "." ++ show t'
  show (TDep e)      = show e
  show (TApp t1 t2)  = "(" ++ show t1 ++ " " ++ show t2 ++ ")"
  show Sort = "*"

data Expr
  = Lit Name
  | TExp Type
  | Abs Name Type Expr
  | TAbs Name Type Expr -- Π 
  | App Expr Expr
  deriving Eq
  -- deriving (Show,Eq)
instance Show Expr where
  show (Lit n)  = n
  show (TExp t) = show t
  show (Abs n t e) = "λ" ++ n ++ ":" ++ show t ++ "." ++ show e
  show (App e1 e2) = "(" ++ show e1 ++ " " ++ show e2 ++ ")"
  show (TAbs n t t') = "λ" ++ n ++ ":" ++ show t ++ "." ++ show t'
type Gamma = [(Name,Type)]
lookup :: Gamma -> Name -> Maybe Type
lookup [] _                      = Nothing
lookup ((n,t):ns) n' | n == n'   = Just t
                     | otherwise = lookup ns n'

subType :: Type -> Name -> Type -> Type
subType newT old (TLit n)      | n == old = newT
subType newT old (TFun t1 t2)             = TFun (subType newT old t1) (subType newT old t2)
subType newT old (TPar n t t') | n /= old = TPar n t (subType newT old t')
subType _ _ t                             = t

accepts :: Gamma -> Type -> Type -> Maybe Type
accepts g (TPar n t t') a | a == t = return $ subType a n t'
accepts g (TFun a b) a' | a == a' = Just b
accepts _ _ _                     = Nothing

tc :: Gamma -> Expr -> Maybe Type
tc g (Lit n)      = lookup g n
tc g (TExp t)     = return t
tc g (Abs n t e)  = tc ((n,t):g) e >>= return . TPar n t
tc g (TAbs n t e) = tc ((n,t):g) e >>= return . TPar n t
tc g (App e1 e2)  = join $ accepts g <$> tc g e1 <*> tc g e2


tint = TLit "int"
tcha = TLit "char"
(a:b:c:d:_) = map (Lit . (:[])) ['a'..'z']

(<>) :: Expr -> Expr -> Expr
(<>) = App

examples :: [Expr]
examples = [
            Abs "a" tcha (Abs "b" tint a),
            a,
            App (Abs "a" (TFun tint tint) a) (Abs "b" tint b),
            Abs "c" tcha (App (Abs "a" tcha (Abs "b" tint a)) c),
            TAbs "A" Sort (Abs "a" (TLit "A") (TExp (TApp (TLit "A") (TDep (Lit "a"))))),
            TAbs "B" Sort (
              Abs "A" 
                (TPar "y" (TLit "B") (TApp (TLit "B")(TDep (Lit "y")))) 
                (Abs "a" (TLit "A") (TExp (TApp (TLit "A") (TDep (Lit "a"))))))
          ]


printExamples :: IO ()
printExamples = mapM_ (\e -> putStrLn $ show e ++ " : " ++ unshow (tc [] e)) examples
  where unshow (Just i) = show i
        unshow Nothing  = "Nothing" 

printExample' = mapM_ (\e -> putStrLn $ show e ++ " : " ++ unshow (tc [] e))
  where unshow (Just i) = show i
        unshow Nothing  = "Nothing" 



test :: IO ()
test = mapM_ (print . tc []) examples
