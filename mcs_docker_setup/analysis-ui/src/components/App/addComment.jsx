import React from 'react';
import { graphql } from 'react-apollo';
import gql from 'graphql-tag';
import TextareaAutosize from 'react-textarea-autosize';

let commentState = {};
let setNeedToRefetch = null;

const AddComment = ({ mutate }) => {
    const submitComment = (evt) => {
        evt.persist();
        mutate({
            variables: { 
                test: commentState.test,
                block: commentState.block,
                submission: commentState.subm,
                performer: commentState.perf,
                createdDate: (new Date()).toISOString(),
                text: document.getElementById("commentTextArea").value,
                userName: document.getElementById("commentUserName").value
            }
        }).then( res => {
            document.getElementById("commentTextArea").value = '';
            document.getElementById("commentUserName").value = '';
            setTimeout(function() {
                setNeedToRefetch(true);
            }, 1500);
        });
    };

    return (
        <div className="commentarea">
            <h5>Leave a comment: </h5>
            <div className="form-group w-50">
                <input type="text" placeholder="Enter name here." id="commentUserName" className="form-control"/>
            </div>
            <div className="form-group w-75">
                <TextareaAutosize id="commentTextArea" minRows={4} cols="100" placeholder="Enter comments here. (Resize for more room)" className="form-control"/>
                <input type="button" onClick={submitComment} value="Submit" className="btn btn-primary mt-2"/>
            </div>
        </div>
    );
};

const addCommentMutation = gql`
    mutation saveComment($test: String!, $block: String!, $submission: String!, $performer: String!, $createdDate: String!, $text: String!, $userName: String!) {
        saveComment(test: $test, block: $block, submission: $submission, performer: $performer, createdDate: $createdDate, text: $text, userName: $userName) {
            text
        }
    }
`;

const AddCommentWithMutation = graphql(addCommentMutation)(AddComment);

class AddCommentBlock extends React.Component {
    render() {
        commentState = this.props.state;
        setNeedToRefetch = this.props.setNeedToRefetch;

        return(
            <AddCommentWithMutation/>
        )
    }
}

export default AddCommentBlock;