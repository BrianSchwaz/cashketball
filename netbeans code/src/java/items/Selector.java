/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package items;

/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */

import java.io.Serializable;
import javax.inject.Named;
import javax.faces.bean.ManagedBean;
import javax.faces.bean.SessionScoped;

/**
 *
 * @author stanchev
 */
@Named(value = "selector")
@ManagedBean
@SessionScoped
public class Selector implements Serializable {

    private String[] choices = {"Create New Customer", "List All Customers", "Find Customer", "Delete Customer"};
    private String choice;

    public String[] getChoices() {
        return choices;
    }

    public void setChoices(String[] choices) {
        this.choices = choices;
    }

    public String getChoice() {
        return choice;
    }

    public void setChoice(String choice) {
        this.choice = choice;
    }

    public String transition() {
        switch (choice) {
            case "Create New Customer":
                return "newCustomer";
            case "List All Customers":
                return "listCustomers";
            case "Find Customer":
                return "findCustomer";
            case "Delete Customer":
                return "deleteCustomer";
            default:
                return null;
        }
    }

}