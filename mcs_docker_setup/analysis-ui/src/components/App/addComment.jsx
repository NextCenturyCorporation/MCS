import React from 'react';
import { graphql } from 'react-apollo';
import gql from 'graphql-tag';
import TextareaAutosize from 'react-textarea-autosize';

let commentState = {};
let setNeedToRefetch = null;

const AddComment = ({ mutate }) => {
    const submitComment = (evt) => {
        evt.persist();
        console.log(commentState);
        mutate({
            variables: { 
                test: commentState.test,
                block: commentState.block,
                submission: commentState.subm,
                performer: commentState.perf,
                createdDate: (new Date()).toISOString(),
                text: document.getElementById("commentTextArea").value
            }
        }).then( res => {
            document.getElementById("commentTextArea").value = '';
            setTimeout(function() {
                setNeedToRefetch(true);
            }, 1500);
        });
    };

    return (
        <div className="commentarea">
            <TextareaAutosize id="commentTextArea" minRows={4} cols="100" defaultValue="Enter comments here.  Resize for more room"/>
            <input type="button" onClick={submitComment} value="Submit"/>
        </div>
    );
};

const addCommentMutation = gql`
    mutation saveComment($test: String!, $block: String!, $submission: String!, $performer: String!, $createdDate: String!, $text: String!) {
        saveComment(test: $test, block: $block, submission: $submission, performer: $performer, createdDate: $createdDate, text: $text) {
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