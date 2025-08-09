/**
 * NERLabeler React Component
 * 
 * A React component for Named Entity Recognition (NER) text labeling.
 * Allows users to select text and assign entity labels interactively.
 * 
 * Features:
 * - Interactive text selection with mouse
 * - Popup label selection modal
 * - Entity highlighting and management
 * - Remove entities functionality
 * 
 * Author: Generated with Claude Code
 * License: MIT
 */

import React, { Component } from 'react';
import PropTypes from 'prop-types';
import './NERLabeler.css';

class NERLabeler extends Component {
    constructor(props) {
        super(props);
        this.state = {
            selectedText: '',
            selectedRange: null,
            showLabelDropdown: false,
            dropdownPosition: { x: 0, y: 0 }
        };
        this.textRef = React.createRef();
    }

    componentDidMount() {
        document.addEventListener('mousedown', this.handleMouseDown);
        document.addEventListener('contextmenu', this.handleContextMenu);
    }

    componentWillUnmount() {
        document.removeEventListener('mousedown', this.handleMouseDown);
        document.removeEventListener('contextmenu', this.handleContextMenu);
    }

    handleMouseDown = (e) => {
        if (!this.textRef.current?.contains(e.target)) {
            this.setState({ showLabelDropdown: false });
        }
    }

    handleContextMenu = (e) => {
        if (!this.textRef.current?.contains(e.target)) return;

        const selection = window.getSelection();
        if (selection.rangeCount === 0 || selection.toString().trim() === '') {
            return;
        }

        e.preventDefault();
        const range = selection.getRangeAt(0);
        const selectedText = selection.toString().trim();

        this.setState({
            selectedText,
            selectedRange: {
                startOffset: this.getAbsoluteOffset(range.startContainer, range.startOffset),
                endOffset: this.getAbsoluteOffset(range.endContainer, range.endOffset)
            },
            showLabelDropdown: true,
            dropdownPosition: { x: e.pageX, y: e.pageY }
        });
    }

    getAbsoluteOffset = (node, offset) => {
        let absoluteOffset = offset;
        let walker = document.createTreeWalker(
            this.textRef.current,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        let currentNode;
        while (currentNode = walker.nextNode()) {
            if (currentNode === node) {
                break;
            }
            absoluteOffset += currentNode.textContent.length;
        }
        return absoluteOffset;
    }

    handleLabelSelection = (labelType) => {
        const { selectedRange, selectedText } = this.state;
        const newEntity = {
            text: selectedText,
            label: labelType,
            start: selectedRange.startOffset,
            end: selectedRange.endOffset,
            id: Date.now() + Math.random()
        };

        const updatedEntities = [...(this.props.entities || []), newEntity];
        
        if (this.props.setProps) {
            this.props.setProps({ entities: updatedEntities });
        }

        this.setState({
            showLabelDropdown: false,
            selectedText: '',
            selectedRange: null
        });

        window.getSelection().removeAllRanges();
    }

    removeEntity = (entityId) => {
        const updatedEntities = this.props.entities.filter(entity => entity.id !== entityId);
        if (this.props.setProps) {
            this.props.setProps({ entities: updatedEntities });
        }
    }

    renderHighlightedText = () => {
        const { text, entities = [] } = this.props;
        if (!text) return null;

        const sortedEntities = [...entities].sort((a, b) => a.start - b.start);
        let result = [];
        let lastIndex = 0;

        sortedEntities.forEach((entity, index) => {
            // Add text before entity
            if (entity.start > lastIndex) {
                result.push(
                    <span key={`text-${index}`}>
                        {text.slice(lastIndex, entity.start)}
                    </span>
                );
            }

            // Add highlighted entity
            result.push(
                <span
                    key={entity.id}
                    className={`ner-entity ner-${entity.label.toLowerCase()}`}
                    title={`${entity.label}: ${entity.text}`}
                    onClick={(e) => {
                        e.stopPropagation();
                        this.removeEntity(entity.id);
                    }}
                    onDoubleClick={(e) => {
                        e.stopPropagation();
                        this.removeEntity(entity.id);
                    }}
                >
                    {entity.text}
                    <span className="ner-label-badge">{entity.label}</span>
                </span>
            );

            lastIndex = entity.end;
        });

        // Add remaining text
        if (lastIndex < text.length) {
            result.push(
                <span key="text-end">
                    {text.slice(lastIndex)}
                </span>
            );
        }

        return result;
    }

    render() {
        const { labelTypes = ['PERSON', 'ORGANIZATION', 'LOCATION', 'MISCELLANEOUS'] } = this.props;
        const { showLabelDropdown, dropdownPosition } = this.state;

        return (
            <div className="ner-labeler-container">
                <div 
                    ref={this.textRef}
                    className="ner-text-container"
                    style={{ userSelect: 'text' }}
                >
                    {this.renderHighlightedText()}
                </div>

                {showLabelDropdown && (
                    <div
                        className="ner-label-dropdown"
                        style={{ left: dropdownPosition.x, top: dropdownPosition.y }}
                    >
                        <select
                            onChange={(e) => {
                                if (e.target.value) {
                                    this.handleLabelSelection(e.target.value);
                                }
                            }}
                            onBlur={() => this.setState({ showLabelDropdown: false })}
                            autoFocus
                        >
                            <option value="">Select label</option>
                            {labelTypes.map(labelType => (
                                <option key={labelType} value={labelType}>
                                    {labelType}
                                </option>
                            ))}
                        </select>
                    </div>
                )}
            </div>
        );
    }
}

NERLabeler.propTypes = {
    id: PropTypes.string,
    text: PropTypes.string.isRequired,
    entities: PropTypes.arrayOf(PropTypes.shape({
        id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
        text: PropTypes.string.isRequired,
        label: PropTypes.string.isRequired,
        start: PropTypes.number.isRequired,
        end: PropTypes.number.isRequired
    })),
    labelTypes: PropTypes.arrayOf(PropTypes.string),
    setProps: PropTypes.func
};

NERLabeler.defaultProps = {
    entities: [],
    labelTypes: ['PERSON', 'ORGANIZATION', 'LOCATION', 'MISCELLANEOUS']
};

export default NERLabeler;