import java.util.List;

import javax.smartcardio.*;

public class NFCReader {
	CardTerminal terminal;
	byte[]data; //data from last read
	
	public NFCReader() {
		data = new byte[256];
	}
	
	/**
	 * Setup card reader
	 * @return true if successful
	 */
	public boolean initialize() {
		TerminalFactory factory = TerminalFactory.getDefault();
		List<CardTerminal> terminals;
		try {
			terminals = factory.terminals().list();
			System.out.println("Terminals: " + terminals);
			
			// get the first terminal
			terminal = terminals.get(0);
		} catch (CardException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return terminal != null;
	}
	
	/**
	 * Attempt to communicate with card. Reads all the data into a buffer if successful.
	 * @return true if successful
	 */
	public boolean tryReadCard() {
		Card card = null;
		boolean success = true;
		try {
			// establish a connection with the card
			card = terminal.connect("*");
			System.out.println("card: " + card);
			CardChannel channel = card.getBasicChannel();
			readIntoBuffer(channel);
			card.disconnect(false);
		} catch (CardException e) {
			success = false;
		} catch(IllegalArgumentException e) {
			success = false; //in case the tag is removed before reading is complete
		}
		return success;
	}
	
	/**
	 * Reads the memory contents into a buffer
	 * @param channel
	 * @throws CardException
	 */
	private void readIntoBuffer(CardChannel channel) throws CardException {
        byte[]command = new byte[4];
        command[0] = 0x30;
        for(int offset = 0; offset <= 41; offset += 4) { //read every 16 bytes (4 words)
        	command[1] = (byte)offset;
        	ResponseAPDU r = channel.transmit(new CommandAPDU(command));
        	byte[]response = r.getBytes();
        	//copy into buffer
        	for(int i = 0; i < 16; ++i) {
        		data[offset*4 + i] = response[i];
        	}
        }
	}
	
	/**
	 * Retrieves serial number from buffer
	 * @return tag serial number
	 */
	public String getSerialNumber() {
		return toHex(data[0]) + toHex(data[1]) + toHex(data[2]) + toHex(data[4]) + toHex(data[5]) + toHex(data[6]) + toHex(data[7]); 
	}
	
	/**
	 * Fetch plaintext tag contents
	 * @return plaintext contents; emptry string if no data
	 */
	public String getContents() {
		int numBytes = data[22];
		if(numBytes <= 7) return ""; //nothing there
		
		String contents = "";
		for(int i = 8; i <= numBytes; ++i) {
			contents += (char)data[22 + i];
		}
		return contents;
	}
	
	/**
	 * Prints out hex bytes of buffer
	 */
	public void dumpRawContents() {
		for(int i = 0; i < data.length; ++i) {
			System.out.print(Integer.toHexString(((int)data[i]) & 0xFF) + " ");
		}
		System.out.println();
	}
	
	public String toHex(byte b) {
		return String.format("%02x", b);
	}
}
