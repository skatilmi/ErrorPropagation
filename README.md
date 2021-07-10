# ErrorPropagation

Python script and notebook to calculate propagation of uncertainties.

There is also a tiny web app written in flask

# Dependencies

- sympy
- Flask if you use the web app

# Usage

this little script gives you the followings things: 1) python code for the expression you can copy directly into your python script 2) python code for the propagated error you can copy directly into your python script 2) on top, you get various latex code for the expressions stated above
parameters:
:expression: enter your expression like you would in python. you can use <variable>\_<index>, to index your variables. You can not use ^
:name: optional, for easier copy and paste, give the function a name
call the following:

```sh
 Errorpropagator(<expression>).showme()
```

# Code example`

```sh
main('a*x+b','lin')
main('a*exp(-(x-m)**2/s**2)', 'gauss')
main('I_0/(((x-x_0)/G)**2+1)+c', 'lorentz')
main('A*exp(-1/(2*s*s)*log(1-Y)**2-s*s/2)', 'func_novosibirsk')
main('A*exp(-s*s/2)', 'H_novosibirsk')
main('a*x*sin(a*x**2)', 'func')
main('sin(a*(x-b))*exp(-x*cos(a*x/50))')
```
