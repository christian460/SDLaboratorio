public class CalculatorImpl extends java.rmi.server.UnicastRemoteObject implements Calculator {
    public CalculatorImpl()
    throws java.rmi.RemoteException {
        super();
    }
    public int add(int a, int b)
    throws java.rmi.RemoteException {
        return a + b;
    }
    public int sub(int a, int b)
    throws java.rmi.RemoteException {
        return a - b;
    }
    public int mul(int a, int b)
    throws java.rmi.RemoteException {
        return a * b;
    }
    public int div(int a, int b)
    throws java.rmi.RemoteException {
        return a / b;
    }
}