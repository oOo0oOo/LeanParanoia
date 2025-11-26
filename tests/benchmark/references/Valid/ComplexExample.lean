-- A more realistic example showcasing various Lean features
-- All components should pass verification

namespace LeanTestProject.Valid.ComplexExample

-- Inductive type definition
inductive Tree (α : Type u) where
  | leaf : α → Tree α
  | node : Tree α → Tree α → Tree α

-- Function definition with pattern matching
def Tree.size {α : Type u} : Tree α → Nat
  | .leaf _ => 1
  | .node left right => left.size + right.size + 1

-- Example with dependent types
def Tree.depth {α : Type u} : Tree α → Nat
  | .leaf _ => 1
  | .node left right => max left.depth right.depth + 1

-- Structure definition (non-recursive to avoid issues)
structure Point where
  x : Nat
  y : Nat

-- Class definition with instance
class Semigroup (α : Type u) where
  op : α → α → α
  op_assoc : ∀ a b c : α, op (op a b) c = op a (op b c)

-- Instance implementation
instance : Semigroup Nat where
  op := (· + ·)
  op_assoc := Nat.add_assoc

-- Polymorphic function
def apply_twice {α : Type u} (f : α → α) (x : α) : α :=
  f (f x)

-- Theorem about our tree size function
theorem tree_size_positive {α : Type u} (t : Tree α) : t.size > 0 := by
  cases t with
  | leaf _ => simp [Tree.size]
  | node left right =>
      have h1 : left.size > 0 := tree_size_positive left
      have h2 : right.size > 0 := tree_size_positive right
      simp [Tree.size]

-- Theorem about tree depth
theorem tree_depth_positive {α : Type u} (t : Tree α) : t.depth > 0 := by
  cases t with
  | leaf _ => simp [Tree.depth]
  | node left right =>
      have h1 : left.depth > 0 := tree_depth_positive left
      have h2 : right.depth > 0 := tree_depth_positive right
      simp [Tree.depth]

-- Theorem relating size and depth (simplified version without omega)
theorem size_ge_one {α : Type u} (t : Tree α) : t.size ≥ 1 := by
  cases t with
  | leaf _ => simp [Tree.size]
  | node _ _ => simp [Tree.size]

-- Using type classes
theorem semigroup_example (a b c : Nat) : (a + b) + c = a + (b + c) :=
  Semigroup.op_assoc a b c

-- Definition with where clause
def fibonacci : Nat → Nat
  | 0 => 0
  | 1 => 1
  | n + 2 => fibonacci n + fibonacci (n + 1)

-- Simple property about fibonacci
theorem fib_0 : fibonacci 0 = 0 := rfl
theorem fib_1 : fibonacci 1 = 1 := rfl
theorem fib_2 : fibonacci 2 = 1 := rfl

-- Using Option type
def safeDivide (n m : Nat) : Option Nat :=
  if m = 0 then none else some (n / m)

theorem safeDivide_zero (n : Nat) : safeDivide n 0 = none := rfl

-- Proof using classical reasoning (whitelisted axioms)
open Classical

theorem decidable_example (P : Prop) : P ∨ ¬P := em P

-- List operations
def List.sum : List Nat → Nat
  | [] => 0
  | x :: xs => x + xs.sum

theorem sum_nil : List.sum [] = 0 := rfl

theorem sum_single (n : Nat) : List.sum [n] = n := by
  simp [List.sum]

-- Using monadic bind
def maybeAdd (mx my : Option Nat) : Option Nat := do
  let x ← mx
  let y ← my
  return x + y

theorem maybeAdd_some (x y : Nat) :
    maybeAdd (some x) (some y) = some (x + y) := rfl

-- Proposition with exists
theorem exists_larger (n : Nat) : ∃ m : Nat, m > n :=
  ⟨n + 1, Nat.lt_succ_self n⟩

end LeanTestProject.Valid.ComplexExample
