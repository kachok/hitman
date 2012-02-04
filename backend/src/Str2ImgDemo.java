//based on https://github.com/callison-burch/crowdsourcing-translation/blob/master/scripts/Str2ImgDemo.java

import java.util.*;
import java.io.*;

import java.awt.*;
import java.awt.font.FontRenderContext;
import java.awt.geom.Rectangle2D;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;

public class Str2ImgDemo
{
  public static Font myFont = new Font("Arial", Font.PLAIN, 18);
  public static FontRenderContext frc = new FontRenderContext(null, true, true);

  static public void main(String[] args) throws Exception
  {
	//fix for indic glyph substitution/ligatures - http://stackoverflow.com/questions/5994815/rendering-devanagari-ligatures-unicode-in-java-swing-jcomponent-on-mac-os-x/6407206#6407206
	if (System.getProperty("os.name").startsWith("Mac OS X")) {
    System.setProperty("apple.awt.graphics.UseQuartz", "true");
}

	  if(args.length < 3) {
		  System.out.println("Usage: java Str2ImgDemo sentenceFile segIdFile outputDir (FontName)");
		  System.exit(0);
	  }
	  String sentenceFile = args[0];
	  String segIdFile = args[1];
	  String outputDir = args[2];
	  if(args.length > 3) {
		  String fontName = args[3];
		  myFont = new Font(fontName, Font.PLAIN, 18);
	  }
	  
	  File dir = new File(outputDir);
	  if (!dir.exists()) {
		  dir.mkdir();
	  }
	  
	  InputStream sentenceStream = new FileInputStream(new File(sentenceFile));
	  BufferedReader sentenceReader = new BufferedReader(new InputStreamReader(sentenceStream, "utf8"));
	  InputStream segIdStream =  new FileInputStream(new File(segIdFile));
	  BufferedReader segIdReader = new BufferedReader(new InputStreamReader(segIdStream, "utf8"));
	  
	  
	  String sentence = sentenceReader.readLine();
	  String segID = segIdReader.readLine();
	  Boolean ltr = true;

	  while (sentence != null) {
		  if (segID.split("-")[1].equals("ltr")){
			ltr=true;
 		}
else{ltr=false;}

		  segID=segID.split("-")[0];
		
		  
		  String imageFilename = Str2ImgDemo.getPath(outputDir, segID + ".png");
		  try {
			  str2img(formatForImage(sentence), 445, 1.5f, imageFilename, ltr);
			  sentence = sentenceReader.readLine();
			  segID = segIdReader.readLine();
		  } catch (Exception e) {
			  System.err.println("Problem creating image " + imageFilename + " for " + sentence);
			  sentence = sentenceReader.readLine();
			  segID = segIdReader.readLine();
		  }
	  }
	  // ccb - this is specific to my translation HITs.
	  String dntFilename = Str2ImgDemo.getPath(outputDir, "do-not-translate.png");
	  str2img("Do not translate this sentence.", 445, 1.5f, dntFilename, true);
	  
	  sentenceReader.close();
	  segIdReader.close();
	  System.exit(0);

  } // main(String[] args)
	
	/**
	 * Cleans up the string so that it can be better rendered as an image.
	 */
	static private String formatForImage(String sentence) {
		sentence = sentence.replace("&nbsp;", " ");
		sentence = sentence.replace("&#160;", " ");
		return sentence;
	}

  static private void str2img(String str, int desiredWidth, float lineSpacing, String outFileName, boolean leftAlign)
  {
    try {

      Vector<String> A = null;
      if (leftAlign) {
        A = splitStr(str,desiredWidth-4);
      } else {
        A = splitStr(str,desiredWidth-11);
      }

      int w = desiredWidth;
      int h = (int)(((A.size() + 0.67)*16.42f)*lineSpacing);

      BufferedImage image = new BufferedImage(w, h, BufferedImage.TYPE_3BYTE_BGR);
      Graphics2D g = image.createGraphics();
      g.setColor(Color.WHITE); // background color
//      g.setColor(new Color(240,240,255)); // background color - very light blue

      g.fillRect(0, 0, w, h);
      g.setColor(Color.BLACK); // text color
//      g.setColor(new Color(220,20,60)); // text color - crimson
//      g.setColor(new Color(0,128,0)); // text color - green
//      g.setColor(new Color(0,0,128)); // text color - navy
      g.setFont(myFont);

      g.setRenderingHint(RenderingHints.KEY_ANTIALIASING,RenderingHints.VALUE_ANTIALIAS_ON);
      FontMetrics fm = g.getFontMetrics(myFont);

      for (int i = 1; i <= A.size(); ++i) {
        String s = A.elementAt(i-1);

        if (leftAlign) {
          g.drawString(s, 0.0f, lineSpacing*i*16.42f); // x = 0
        } else {
          Rectangle2D bounds = fm.getStringBounds(s, g);
          int textWidth  = (int)(bounds.getWidth());
          g.drawString(s, desiredWidth - textWidth, lineSpacing*i*16.42f); // x > 0, especially for last line
        }
      }

      g.dispose();

      File file = new File(outFileName);
      ImageIO.write(image,"png",file);

    } catch (FileNotFoundException e) {
      System.err.println("FileNotFoundException in str2img(...): " + e.getMessage());
      System.exit(99901);
    } catch (IOException e) {
      System.err.println("IOException in str2img(...): " + e.getMessage());
      System.exit(99902);
    }
  }

  static private Vector<String> splitStr(String str, int width)
  {
    Vector<String> subStrs = new Vector<String>();
    String[] words = str.split(" ");    

    int i = 0; // number of words processed

    while (i < words.length) {
      String nextStr = words[i];
      String nextStrCand = words[i];
      ++i;
      int currWidth = (int)myFont.getStringBounds(nextStr,frc).getWidth();

      while (i < words.length) {
        nextStrCand += " " + words[i];
        int candWidth = (int)myFont.getStringBounds(nextStrCand,frc).getWidth();
        if (candWidth <= width) {
          nextStr = nextStrCand;
          currWidth = candWidth;
          ++i;
        } else {
          break;
        }
      }

      subStrs.add(nextStr);

    }

    return subStrs;
  }

	
	
	/** 
	 * @return the full path filename of the filename in the directory.
	 */
	public static String getPath(String directory, String filename) {
		File file = new File(directory, filename);
		return file.getAbsolutePath();
	}
	
}