{-# LANGUAGE GADTs, DeriveFunctor #-}

import Prelude hiding (lookup)

data Lam id
  = Lit id
  | Lam id (Lam id)
  | App (Lam id) (Lam id)
  deriving Functor


instance Show a => Show (Lam a) where
  show (Lit a) = show a
  show (Lam n e) = "λ" ++ show n ++ "." ++ show e
  -- show (Lam n e) = "\\lam " ++ show n ++ "." ++ show e
  show (App (Lit a1) (Lit a2)) = show a1 ++ " " ++ show a2
  show (App a1 (App a2 a3))    = show a1 ++ " (" ++ show (App a2 a3) ++ ")"
  show (App (Lam n1 e1) (Lam n2 e2))       = "(" ++ show (Lam n1 e1) ++ ") (" ++ show (Lam n2 e2) ++ ")"
  show (App (Lam n e) a)       = "(" ++ show (Lam n e) ++ ") " ++ show a
  show (App a (Lam n e))       = show a ++ "(" ++ show (Lam n e) ++ ") " 

  show (App a1 a2) = show a1 ++ " " ++ show a2 -- "(" ++ show a1 ++ ") (" ++ show a2 ++ ")"

newtype String' = S' String deriving Eq
instance Show String' where { show (S' s) = s }


y = fmap S' $ Lam "f" (App (Lam "x" (App (Lit "f") (App (Lit "x") (Lit "x")))) (Lam "x" (App (Lit "f") (App (Lit "x") (Lit "x")))))
x = fmap S' $ Lit "fac"

t1 = fmap S' $ Lam "w" (Lit "y")
t2 = fmap S' $ Lit "w"

-- Y e |-> e (Y e)

data Sem id
  = LetIn id (Sem id) (Sem id)
  | Val (Lam id)

instance Show a => Show (Sem a) where
  show (LetIn n v e) = "(let " ++ show n ++ " = " ++ show v ++ " in " ++ show e ++ ")"
  show (Val e)       = show e

conv :: Lam id -> Sem id
conv (App (Lam id e) a) = LetIn id (conv a) (conv e)
-- sem (Lam id e) = Val (Lam id (sem e))
conv a = Val a

type MapStack k v = [(k,v)]
lookup :: Eq k => k -> MapStack k v -> v
lookup _ [] = undefined
lookup k' ((k,v):stk) | k' == k   = v
                      | otherwise = lookup k' stk

fv :: Eq a => Lam a -> [a]
fv e = fv' e []
  where fv' (Lit a) bound     = if a `elem` bound then [] else [a]
        fv' (Lam a e) bound   = fv' e (a:bound)
        fv' (App e1 e2) bound = (fv' e1 bound) ++ (fv' e2 bound)

new :: Eq a => [a] -> Lam a -> a
new alp e = head $ filter (not . flip elem (fv e)) alp

sub :: Eq a => [a] -> a -> Lam a -> Lam a -> Lam a
sub _ a e (Lit a')                  = if a == a' then e else Lit a'
sub alp a e (App e1 e2)             = App (sub alp a e e1) (sub alp a e e2)
sub alp a e (Lam a' e')             = Lam a'' (sub (drop 1 alp) a e (sub (drop 1 alp) a' (Lit a'') e'))
  where used   = a : a' : (fv e ++ fv e' ++ fv (Lam a' e'))
        unused = filter (not . flip elem used) alp
        a''    = new unused (Lam a' e')
-- sub alp a e (Lam a' e') | a == a'   = let used = a : (fv e ++ fv (Lam a' e'))
--                                           in let a''  = new (filter (not . flip elem used) alp) (Lam a' e')
--                                                  in Lam a'' (sub alp a' e (sub alp a' (Lit a'') e'))
--                         | otherwise = Lam a' (sub alp a e e')

alphabet = map (S' . (:[])) ['a'..'z']

sem :: Eq a => [a] -> Lam a -> Lam a
sem alp (App (Lam v e) e') = (sem alp (sub alp v e' (sem alp e)))
sem alp (App (App e1 e2) e3) = sem alp (App (sem alp (App e1 e2)) e3)
sem alp a = a


sem' :: Eq a => [a] -> Lam a -> Int -> (Lam a,Int)
sem' _ a (-1) = (a,0)
sem' _ a 0    = (a,0)
-- sem' alp (Lam v e) n = (Lam v e',n')
--   where (e',n') = sem' alp' e n
--         alp' = filter (not . (==) v) alp

sem' alp (App (Lam v e) e') n   = sem' alp' (sub alp' v e' e) (n-1)
  where alp' = filter (not . (==) v) (drop 1 alp)
sem' alp (App (App e1 e2) e3) n = sem' (drop n' alp) (App e' e3) n'
  -- where (e',n') = sem' (drop 1 alp) (App e1 e2) n -- To only count beta reductions
  where (e',n') = sem' (drop 1 alp) (App e1 e2) (n-1) -- To show each step


sem' alp (App e1 e2) n = ((App e1' e2'),n2')
  where (e1',n1') = sem' alp e1 n
        (e2',n2') = sem' alp e2 n1'

sem' alp a n                    = (a,n)

-- a a
probA = fmap S' $ App (App (Lam "z" (Lit "z")) (Lam "y" (App (Lit "y") (Lit "y")))) (Lam "x" (App (Lit "x") (Lit "a")))
-- b b
probB = fmap S' $ App (App (Lam "x" (Lam "y" (App (App (Lit "x") (Lit "y")) (Lit "y")))) (Lam "a" (Lit "a"))) (Lit "b")
-- y z
probC = fmap S' $ App (App (Lam "x" (Lam "y" (App (Lit "x") (Lit "y")))) (Lit "y")) (Lit "z")
-- λc.y y c
probD = fmap S' $ App (App (Lam "x" (Lam "z" (App (Lit "x") (Lit "y")))) (Lam "x" (Lam "z" (App (App (Lit "x") (Lit "y")) (Lit "z"))))) (Lam "x" (Lit "z"))

format exps = mapM_ putStrLn $ map ( (\s -> "\\mapsto \\ & " ++ s ++ "\\\\") . show . fst) exps

prob5 = fmap S' $ (let t = (Lam "x" (App (App (Lit "x") (Lit "x")) (Lit "y"))) in App t t)


true'  = (Lam "x" (Lam "y" (Lit "x")))
false' = (Lam "x" (Lam "y" (Lit "y")))
true = fmap S' $ true'
false = fmap S' $ false'
not'  =fmap S' $ Lam "x" (App (App (Lit "x") false') true')
or'   =fmap S' $ (Lam "x" (Lam "y" (App (App (Lit "x") true') (Lit "y"))))
