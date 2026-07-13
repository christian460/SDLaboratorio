import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.ArrayList;
import java.util.List;

class Message {
    int sender;
    int timestamp;

    public Message(int sender, int timestamp) {
        this.sender = sender;
        this.timestamp = timestamp;
    }
}

class ProcessNode extends Thread {

    private int id;
    private int clock;
    private List<ProcessNode> processes;
    private BlockingQueue<Message> inbox;

    public ProcessNode(int id) {
        this.id = id;
        this.clock = 0;
        this.inbox = new LinkedBlockingQueue<>();
    }

    public void setProcesses(List<ProcessNode> processes) {
        this.processes = processes;
    }

    public synchronized void localEvent() {
        clock++;
        System.out.println("Proceso " + id +
                " ejecuta evento local. Tiempo = " + clock);
    }

    public synchronized void sendMessage(ProcessNode receiver) {
        clock++;
        Message msg = new Message(id, clock);
        System.out.println("Proceso " + id +
                " envia mensaje a Proceso " +
                receiver.id +
                " con tiempo " + clock);
        receiver.receive(msg);
    }

    public void receive(Message msg) {
        inbox.add(msg);
    }

    private synchronized void processMessage(Message msg) {
        clock = Math.max(clock, msg.timestamp) + 1;
        System.out.println("Proceso " + id +
                " recibe mensaje de Proceso " +
                msg.sender +
                ". Tiempo recibido = " +
                msg.timestamp +
                " -> Nuevo reloj = " +
                clock);

    }

    @Override
    public void run() {

        try {
            localEvent();
            Thread.sleep((long)(Math.random()*500));
            ProcessNode receiver =
                    processes.get((id+1)%processes.size());
            sendMessage(receiver);
            Thread.sleep((long)(Math.random()*500));

            while(!inbox.isEmpty()){
                processMessage(inbox.take());
            }

            localEvent();

        } catch(Exception e){
            e.printStackTrace();
        }
    }
}

public class LamportDistributedSimulation {
    public static void main(String[] args) throws Exception {
        int n = 5;
        List<ProcessNode> processes = new ArrayList<>();

        for(int i=0;i<n;i++){
            processes.add(new ProcessNode(i));
        }

        for(ProcessNode p:processes){
            p.setProcesses(processes);
        }

        for(ProcessNode p:processes){
            p.start();
        }

        for(ProcessNode p:processes){
            p.join();
        }
        System.out.println("\nSimulacion finalizada.");
    }
}
