{-# LANGUAGE GADTs, DeriveFunctor #-}

import qualified Data.Map as M
import Data.Map (Map)
import Prelude hiding (lookup)

data Lam id
  = Var id
  | Abs id (Lam id)
  | App (Lam id) (Lam id)
  deriving Functor


instance Show a => Show (Lam a) where
  show (Var a) = show a
  show (Abs n e) = "λ" ++ show n ++ "." ++ show e
  -- show (Abs n e) = "\\Abs " ++ show n ++ "." ++ show e
  show (App (Var a1) (Var a2)) = show a1 ++ " " ++ show a2
  show (App a1 (App a2 a3))    = show a1 ++ " (" ++ show (App a2 a3) ++ ")"
  show (App (Abs n1 e1) (Abs n2 e2))       = "(" ++ show (Abs n1 e1) ++ ") (" ++ show (Abs n2 e2) ++ ")"
  show (App (Abs n e) a)       = "(" ++ show (Abs n e) ++ ") " ++ show a
  show (App a (Abs n e))       = show a ++ "(" ++ show (Abs n e) ++ ") " 

  show (App a1 a2) = show a1 ++ " " ++ show a2 -- "(" ++ show a1 ++ ") (" ++ show a2 ++ ")"

newtype String' = S' String deriving Eq
instance Show String' where { show (S' s) = s }


type Expr = Lam String
data Type = U Int | Fun Type Type deriving Eq
type TypeRelation = (Expr,Type)
type Gamma = [TypeRelation]
baseTy = U 0

instance Show Type where
  show (U i) = "u" ++ show i 
  show (Fun t1 t2) = show t1 ++ " -> " ++ show t2


data Hole 
  = Hole
  | FunHole Hole Hole deriving (Eq,Show)
-- instance Show Hole where
--   show Hole = " _ "
--   show (FunHole e1 e2) = "" ++ show e1 ++ " -> (" ++ show e2 ++ ")"

-- data ASTStruct id
--   = Var id
--   | Abs id (Lam id)
--   | App (Lam id) (Lam id)
--   deriving Functor

-- gamFind :: Expr -> [(Expr,Hole)]
-- gamFind e@(Var x) = (e, tyFind e) : []
-- gamFind e@(App e1 e2) = (e, tyFind e) : (e1 )
-- tyFind :: Expr -> Hole
-- tyFind (Var x)     = Hole -- error "free variable [ " ++ x ++ " ] cannot be typed."
-- -- tyFind (App e1 e2) = 
-- tyFind (Abs v e2) = FunHole (tyFind e1) (tyFind e2)


type MapStack k v = [(k,v)]

lookup :: Eq k => k -> MapStack k v -> Maybe v
lookup _ [] = Nothing
lookup k' ((k,v):stk) | k' == k   = Just v
                      | otherwise = lookup k' stk

-- data ProofBranch = PB (Expr,Hole) [ProofBranch]
-- findProofBranch :: (MapStack Expr Hole Expr,Int) -> Expr -> (MapStack Expr Hole Expr,Int)
-- findProofBranch (g,n) e@(Var x) = ((e,lookup (Hole n) e g):g,n + 1)
-- findProofBranch (g,n) e@(App e1 e2) = ((e,lookup (Hole n) e g))
--   where (g',n')   = findProofBranch (g,n + 1) e1
--         (g'',n'') = findProofBranch (g',n') e2

type Name = String

findRequiredGamma :: MapStack Name Type -> Expr -> MapStack Name Hole
findRequiredGamma g e@(Var x) = case lookup x g of 
                                (Just _) -> []
                                _ -> (x,Hole):[]

findRequiredGamma g e@(App e1 e2) = findRequiredGamma g e1 ++ findRequiredGamma g e2
findRequiredGamma g e@(Abs v e1) = findRequiredGamma ((v,U (length g)):g) e1

-- tc :: Gamma -> Expr -> Type



y :: a
y = y
x :: a
x = x