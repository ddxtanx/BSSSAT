# Mathematical background
In this repo we're trying to solve for differentials in a spectral sequence (the rho-Bockstein spectral sequence) using a SAT solver.
The E_1 page of the spectral sequence is Ext_{AC}(F_2[tau], F_2[tau])[rho], where the power of rho is the spectral sequence filtration, and Ext_{AC} is computed in a large range and imported into this computation (the "machine" csv-- ignore the non-machine one).
Differentials increase powers of rho, but for bookkeeping purposes we hide the power of rho, writing d_r(x)= y instead of d_r(x)=rho^r y.

For each degree, d_r is a F_2-linear map, and the goal is to determine the entries of the matrix. These are the variables in the SAT problem.
The constraints come from structural facts about the spectral sequence (e.g. if d_r(x)=y then d_i(y)=0 for all i), linearity, as well as the Leibniz rule (currently unimplemented).



# Status
The next major step is to implement the Leibniz rule, d_r(x*y) = d_r(x)*y + x*d_r(y).
Right now we don't have a list of all products x*y, but we do know that tau-multiplication works the way the names suggest, except some elements have tau^n x = 0.
tau-torsion is recorded in the Ext_{AC} table, though there is a possibility that tau * x and tau * y are nonzero (for x,y basis elements) but tau * (x+y) = 0. I'm not sure if we've handled this yet; it will require outside information. However, this is unlikely to happen in the range we care about.
The next step is to implement the Leibniz rule just for tau-multiplication.
tau is not a permanent cycle, but d_r(tau^{2^r}) = rho^{2^r}tau^{2^{r-1}} h_r (but we're omitting the rho-powers).
This means that we can just consider the products tau^{2^r} x, where x could have tau-multiples in front of it:
* if r < i, this is d_r(tau^{2^i} * x) = tau^{2^i} d_r(x) where x could be a class with tau-multiples in front of it.
* if r = i, this is d_r(tau^{2^r} * x) = tau^{2^{r-1}} * h_r * x + tau^{2^r} * d_r(x).
