/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package fillstats;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.Arrays;
import java.util.HashMap;

import java.sql.Connection;
import java.sql.Date;
import java.sql.PreparedStatement;
import java.sql.ResultSet;

import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;

/**
 *
 * @author bkschwar
 */
public class CSVReader {
    
    ArrayList<String> fields;
    ArrayList<HashMap<String,String>> data = new ArrayList<HashMap<String,String>>();
    String filename;
    BufferedReader br = null;
    String line = "";
    String csvSplitBy = ",";
    File file;
    private DBConnect dbConnect = new DBConnect();
    private Date created_date;
    String table = "";
    
    CSVReader(String filename){
        this.filename = filename;
        this.table = filename.replace(".csv", "");
        this.file = new File(filename);
    }
    
    public void getHeaders()
    {
        try 
        {
            br = new BufferedReader(new FileReader(filename));
            line = br.readLine();
            String[] headers = line.split(csvSplitBy);
            fields = new ArrayList<String>(Arrays.asList(headers));
            //System.out.println(Arrays.toString(headers) + "***");
        }
        catch(FileNotFoundException e)
        {
            System.out.println(filename + " not found");
        } 
        catch(IOException e){
            e.printStackTrace();
        }
    }
    
    public void getData()
    {
        try 
        {
            String[] datalines;
            while((line = br.readLine()) != null)
            {
                datalines = line.split(csvSplitBy,-1);
                System.out.println(Arrays.toString(datalines));
                /*if(line.charAt(line.length() - 1) == ',')
                {
                    line = line + ",";
                }*/
                //System.out.println(Arrays.toString(data));
                HashMap<String,String> dataHash = new HashMap<String,String>();
                for(int i = 0;i < fields.size();i++)
                {
                    dataHash.put(fields.get(i),datalines[i]);
                    //System.out.print(data[i] + ",");
                }
                //System.out.println("***");
                data.add(dataHash);
            }
        }
        catch(FileNotFoundException e)
        {
            System.out.println(filename + " not found");
        } 
        catch(IOException e){
            e.printStackTrace();
        }
    }
    
    public String getQuestionMarks()
    {
        String questionMarks = "";
        for(int i = 0; i < fields.size();i++)
        {
            if(i == 0)
            {
                questionMarks += "?";
            }
            else
            {
                questionMarks += ",?";
            }
        }
        return questionMarks;
    }
    
    public String getFields()
    {
        String fieldString = "";
        for(int i = 0; i < fields.size();i++)
        {
            if(i == 0)
            {
                fieldString += fields.get(i);
            }
            else
            {
                fieldString += "," + fields.get(i);
            }
        }
        return fieldString;
    }
    
    public void insertData() throws SQLException
    {
        Connection con = dbConnect.getConnection();
        if (con == null) {
            throw new SQLException("Can't get database connection");
        }
        con.setAutoCommit(false);

        PreparedStatement ps
                = con.prepareStatement(
                        "SELECT column_name,data_type FROM information_schema.columns WHERE table_name = '" + table + "'");

        //get Player data from database
        ResultSet result = ps.executeQuery();
        
        HashMap<String,String> fieldlist = new HashMap<String,String>();

        while (result.next()) {
            String col_name = result.getString("column_name");
            String data_type = result.getString("data_type");
            System.out.println(table + " " + col_name + " " + data_type);
            fieldlist.put(col_name,data_type);
        }
        
        result.close();
        System.out.println(data.size());
        Statement deleteStatement = con.createStatement();
        deleteStatement.executeUpdate("DELETE FROM \"" + table +  "\" *;");
        deleteStatement.executeUpdate("DELETE FROM \"Player\" *;");
        deleteStatement.close();
        con.commit();
        
        //Statement statement = con.createStatement();
        /*PreparedStatement pStatement = con.prepareStatement("INSERT INTO \"Player\" (name,pid,weight,height) VALUES (?,?,?,?);");
        pStatement.setInt(2, 0);
        pStatement.setString(1,"Russell Westbrook");
        pStatement.setInt(3,200);
        pStatement.setInt(4,74);
        pStatement.executeUpdate();
        //statement.close();
        con.commit();*/
        PreparedStatement preparedStatement;
        for(int i = 0; i < data.size();i++)
        {
            
            String prepStatement = "INSERT INTO \"" + table + "\" (" + getFields() + ") VALUES (" + getQuestionMarks() +");";
            System.out.println(prepStatement);
            preparedStatement = con.prepareStatement(prepStatement);
            for(int j = 0; j < fields.size();j++)
            {
                String type = fieldlist.get(fields.get(j));
                System.out.println(type + " " + data.get(i).get(fields.get(j)));
                String value = data.get(i).get(fields.get(j));
                if(type.equals("integer"))
                {
                    if(value.equals(""))
                    {
                        preparedStatement.setNull(j+1,java.sql.Types.INTEGER);
                    }
                    else
                    {
                        try {
                           preparedStatement.setInt(j+1, Integer.parseInt(value)); 
                           //System.out.println("int");
                        }catch (NumberFormatException e) {
                            throw e;
                        }
                    }
                }
                else if(type.equals("real"))
                {
                    if(value.equals(""))
                    {
                        preparedStatement.setNull(j+1,java.sql.Types.FLOAT);
                    }
                    else
                    {
                        try {
                           preparedStatement.setFloat(j+1, Float.parseFloat(value)); 
                           //System.out.println("real");
                        }catch (NumberFormatException e) {
                            throw e;
                        }
                    }
                }
                else if(type.equals("text"))
                {
                    preparedStatement.setString(j+1, value);
                    //System.out.println("text");
                } 
            }
            preparedStatement.executeUpdate();
            preparedStatement.close();
            
        }
        //Util.invalidateUserSession();
        con.commit();
        con.close();
    }
}
