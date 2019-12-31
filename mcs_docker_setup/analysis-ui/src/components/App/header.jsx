import React from 'react';
import { Query } from 'react-apollo';
import gql from 'graphql-tag';
import _ from "lodash";
import Navbar from 'react-bootstrap/Navbar';
import Nav from 'react-bootstrap/Nav';
import NavDropdown from 'react-bootstrap/NavDropdown';

const GET_FIELD_AGG = gql`
    query getFieldAggregation($fieldName: String!){
        getFieldAggregation(fieldName: $fieldName) {
            key
        }
  }`;

class ListItem extends React.Component {
    render() {
        this.props.state[this.props.stateName] = this.props.item;
        
        const urlBasePath = window.location.href.split('?')[0];
        const params = "?perf=" + this.props.state["perf"] + "&subm=" + this.props.state["subm"] + "&block=" + this.props.state["block"] + "&test=" + this.props.state["test"];

        const newLocation = urlBasePath + params;

        return (
            <NavDropdown.Item id={this.props.stateName + "_" + this.props.itemKey} href={newLocation}>{this.props.item}</NavDropdown.Item>
        )
    }
}

class DropListItems extends React.Component {
    render() {
        return(
            <Query query={GET_FIELD_AGG} variables={{"fieldName": this.props.fieldName}}>
            {
                ({ loading, error, data }) => {
                    let dropdownOptions = [];

                    if(data !== undefined) {
                        dropdownOptions = _.map(data["getFieldAggregation"], 'key');
                    } 

                    return (
                        dropdownOptions.map((item,key) =>
                            <ListItem stateName={this.props.stateName} state={this.props.state} item={item} itemKey={key}/>
                        )
                    )
                }
            }
            </Query>
        );
    }
}

class EvalHeader extends React.Component {
    render() {
        return (
            <Navbar variant="dark" expand="lg">
                <Navbar.Brand href="#home">MCS Analysis</Navbar.Brand>
                <Navbar.Toggle aria-controls="basic-navbar-nav" />
                <Navbar.Collapse id="basic-navbar-nav">
                    <Nav className="mr-auto">
                    <NavDropdown title={"Performer: " + this.props.state.perf} id="basic-nav-dropdown">
                        <DropListItems fieldName={"performer"} stateName={"perf"} state={this.props.state}/>
                    </NavDropdown>
                    <NavDropdown title={"Submission: " + this.props.state.subm} id="basic-nav-dropdown">
                        <DropListItems fieldName={"submission"} stateName={"subm"} state={this.props.state}/>
                    </NavDropdown>
                    <NavDropdown title={"Block: " + this.props.state.block} id="basic-nav-dropdown">
                        <DropListItems fieldName={"block"} stateName={"block"} state={this.props.state}/>
                    </NavDropdown>
                    <NavDropdown title={"Test: " + this.props.state.test} id="basic-nav-dropdown">
                        <DropListItems fieldName={"test"} stateName={"test"} state={this.props.state}/>
                    </NavDropdown>
                    </Nav>
                </Navbar.Collapse>
            </Navbar>
        );
    }
}

export default EvalHeader;
